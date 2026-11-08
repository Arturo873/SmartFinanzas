"""
Vistas de la Capa de Presentación Gerencial (Dashboard).
SmartFinanzas - Arquitectura Monolito Modular.

Esta app NO define modelos propios. Inyecta dependencias
de lectura de moduloETL, moduloTransaccional y capaAnalitica para renderizar
el panel gerencial interactivo y emitir informes ejecutivos en PDF.
"""

import io
import json
import logging
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Q
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

# Dependencias de lectura de las otras aplicaciones del monolito
from usuarios.models import Usuario, Empresa
from AppWeb.models import PerfilUsuario
from moduloETL.models import RatioFinanciero, CargaFinanciera
from moduloETL.services import detectar_anomalias_financieras
from moduloTransaccional.models import Venta
from capaAnalitica.models import PrediccionRiesgo
from capaAnalitica.services import MotorRiesgo, ejecutar_y_persistir_prediccion, VARIABLES_FINANCIERAS
from .pdf_generator import construir_informe_ejecutivo_pdf

logger = logging.getLogger(__name__)


def resolver_usuario_bd(auth_user):
    """
    Obtiene la entidad Usuario del sistema a partir del usuario Django en sesión con caché en memoria.
    """
    if not auth_user or not auth_user.is_authenticated:
        return None
    if isinstance(auth_user, Usuario):
        return auth_user
    if hasattr(auth_user, '_cached_usuario_db'):
        return auth_user._cached_usuario_db

    usuario_db = Usuario.objects.select_related('empresa', 'rol').filter(username=auth_user.username).first()
    if not usuario_db and hasattr(auth_user, 'email'):
        usuario_db = Usuario.objects.select_related('empresa', 'rol').filter(email=auth_user.email).first()

    auth_user._cached_usuario_db = usuario_db
    return usuario_db


class DashboardRolMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Control de acceso RBAC estricto: restringe la visualización del Dashboard
    únicamente a los roles pertinentes (Dueño, Contador y Administrador).
    """
    roles_permitidos = ['Dueño', 'Contador', 'Administrador']
    login_url = 'usuarios:login'

    def get_user_role(self):
        user = self.request.user
        if not user.is_authenticated:
            return None

        # 1. PerfilUsuario en AppWeb
        if hasattr(user, 'perfil') and user.perfil and hasattr(user.perfil, 'rol'):
            return user.perfil.rol

        # 2. Modelo Usuario en usuarios
        usuario_db = resolver_usuario_bd(user)
        if usuario_db and usuario_db.rol:
            return usuario_db.rol.nombre

        # 3. Sesión HTTP
        return self.request.session.get('usuario_rol')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        rol = self.get_user_role()
        return rol in self.roles_permitidos

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Acceso restringido: El Panel Gerencial está reservado únicamente para Dueños y Contadores."
            )
            return redirect('principal')
        return super().handle_no_permission()


class DashboardView(DashboardRolMixin, TemplateView):
    """
    Controlador principal de la Capa de Presentación Gerencial.
    Realiza consultas de solo lectura a los modelos de otras aplicaciones
    para poblar el Semáforo de Riesgo, el Panel de Explicabilidad SHAP,
    la Curva de Tendencia y el Resumen Operativo de Ventas.
    """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        usuario_db = resolver_usuario_bd(user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # 1. Filtrado Multi-tenant para PrediccionRiesgo (capaAnalitica)
        predicciones_qs = PrediccionRiesgo.objects.select_related('ratio', 'empresa', 'ejecutada_por_usuario')
        if empresa_usuario:
            predicciones_qs = predicciones_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            predicciones_qs = predicciones_qs.none()

        # Selección de predicción activa: permite al usuario hacer clic en un punto de la curva
        # o seleccionar un período para actualizar todos los datos del dashboard.
        prediccion_id_param = (self.request.GET.get('prediccion_id') or '').strip()
        periodo_param = (self.request.GET.get('periodo') or '').strip()

        prediccion_seleccionada = None
        if prediccion_id_param and prediccion_id_param.isdigit():
            prediccion_seleccionada = predicciones_qs.filter(id=int(prediccion_id_param)).first()

        if not prediccion_seleccionada and periodo_param:
            prediccion_seleccionada = predicciones_qs.filter(
                Q(ratio__periodo=periodo_param) | Q(ratio__periodo__icontains=periodo_param)
            ).order_by('-fecha_prediccion', '-id').first()

        mas_reciente_db = predicciones_qs.order_by('-fecha_prediccion', '-id').first()
        ultima_prediccion = prediccion_seleccionada or mas_reciente_db
        es_prediccion_mas_reciente = bool(
            ultima_prediccion and mas_reciente_db and ultima_prediccion.id == mas_reciente_db.id
        )

        score = float(ultima_prediccion.score_riesgo) if (ultima_prediccion and ultima_prediccion.score_riesgo is not None) else None
        nivel = ultima_prediccion.nivel_semaforo if ultima_prediccion else 'Sin Datos'
        fecha_prediccion = ultima_prediccion.fecha_prediccion if ultima_prediccion else None

        # 2. Extracción de variables SHAP almacenadas en la predicción
        top_3_variables = []
        if ultima_prediccion and ultima_prediccion.variables_influyentes:
            try:
                top_3_variables = json.loads(ultima_prediccion.variables_influyentes)
            except Exception:
                top_3_variables = []

        # 3. Consulta de predicciones históricas para la curva de tendencia (RF-04)
        # Extraer todos los períodos históricos disponibles para los filtros
        periodos_disponibles = []
        for p in predicciones_qs:
            per = p.ratio.periodo if (p.ratio and p.ratio.periodo) else (p.fecha_prediccion.strftime('%d/%m/%Y') if p.fecha_prediccion else f"#{p.id}")
            if per and per not in periodos_disponibles:
                periodos_disponibles.append(per)
            periodos_disponibles.sort()

        # Hasta 20 evaluaciones históricas para graficación y filtrado dinámico (RF-04)
        predicciones_curva = predicciones_qs
        if periodo_param:
            predicciones_curva = predicciones_curva.filter(
                Q(ratio__periodo=periodo_param) | Q(ratio__periodo__icontains=periodo_param)
            )
        ultimas_predicciones = list(predicciones_curva.order_by('-fecha_prediccion', '-id')[:20])
        # Invertir a orden cronológico ascendente para el eje horizontal del gráfico
        predicciones_cronologicas = list(reversed(ultimas_predicciones))

        chart_fechas = [
            f"{p.ratio.periodo} ({p.fecha_prediccion.strftime('%d/%m %H:%M')})" if (p.ratio and p.ratio.periodo and p.fecha_prediccion)
            else (p.fecha_prediccion.strftime('%d/%m %H:%M') if p.fecha_prediccion else f"#{p.id}")
            for p in predicciones_cronologicas
        ]
        chart_scores = [
            float(p.score_riesgo or 0.0)
            for p in predicciones_cronologicas
        ]
        chart_niveles = [
            p.nivel_semaforo or ('Rojo' if (p.score_riesgo or 0) > 70 else 'Amarillo' if (p.score_riesgo or 0) > 35 else 'Verde')
            for p in predicciones_cronologicas
        ]
        chart_es_actual = [
            bool(ultima_prediccion and p.id == ultima_prediccion.id)
            for p in predicciones_cronologicas
        ]
        if ultima_prediccion and chart_es_actual and not any(chart_es_actual):
            chart_es_actual[-1] = True

        # Estructura enriquecida por punto para interactividad completa en el frontend (RF-04)
        chart_puntos = [
            {
                'id': p.id,
                'periodo': p.ratio.periodo if (p.ratio and p.ratio.periodo) else (p.fecha_prediccion.strftime('%d/%m/%Y') if p.fecha_prediccion else f"#{p.id}"),
                'fecha_corta': p.fecha_prediccion.strftime('%d/%m %H:%M') if p.fecha_prediccion else '',
                'fecha_completa': p.fecha_prediccion.strftime('%d/%m/%Y %H:%M') if p.fecha_prediccion else '',
                'label': chart_fechas[i],
                'score': chart_scores[i],
                'nivel': chart_niveles[i],
                'es_actual': chart_es_actual[i],
            }
            for i, p in enumerate(predicciones_cronologicas)
        ]

        # 4. Total Ingreso_Real del día actual sumando transacciones de Venta (moduloTransaccional / app_caja)
        hoy = timezone.localdate()
        ventas_hoy_qs = Venta.objects.filter(fecha__date=hoy)
        if empresa_usuario:
            ventas_hoy_qs = ventas_hoy_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            ventas_hoy_qs = ventas_hoy_qs.none()

        ingreso_real_hoy = ventas_hoy_qs.aggregate(total=Sum('ingreso_real'))['total'] or Decimal('0.00')
        total_ventas_hoy = ventas_hoy_qs.count()

        # Ratios disponibles para ejecutar predicción si se desea
        ratios_qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            ratios_qs = ratios_qs.none()

        ultimo_ratio = (
            ultima_prediccion.ratio
            if (ultima_prediccion and ultima_prediccion.ratio)
            else ratios_qs.order_by('-fecha_calculo', '-id').first()
        )

        # Detección de valores anómalos (outliers) en el balance activo (RF-10)
        anomalias_detectadas = detectar_anomalias_financieras(ultimo_ratio) if ultimo_ratio else []
        tiene_anomalias = bool(anomalias_detectadas)

        # Ratios de la predicción activa para trazabilidad integral de los resultados (X1 a X7)
        ratio_asociado_prediccion = ultimo_ratio
        todos_los_ratios_prediccion = []

        METADATA_ADICIONAL_RATIOS = {
            'X1': {'formula': 'Activo Corriente / Pasivo Corriente', 'meta': '> 1.50x'},
            'X2': {'formula': 'Capital de Trabajo / Activo Total', 'meta': '> 0.0%'},
            'X3': {'formula': 'Pasivo Total / Patrimonio Neto', 'meta': '< 1.00x'},
            'X4': {'formula': 'Utilidad Operacional / Activo Total', 'meta': '> 5.0%'},
            'X5': {'formula': 'Utilidad Operacional / Ventas Netas', 'meta': '> 10.0%'},
            'X6': {'formula': 'Ventas Netas / Activo Total', 'meta': '> 1.00x'},
            'X7': {'formula': 'Desviación Flujo Diario / Flujo Medio', 'meta': 'Baja dispersión'},
        }

        shap_dict = {}
        if ultima_prediccion and ultima_prediccion.impacto_variables:
            try:
                raw_impacto = json.loads(ultima_prediccion.impacto_variables)
                if isinstance(raw_impacto, dict):
                    shap_dict = raw_impacto
                elif isinstance(raw_impacto, list):
                    shap_dict = {item.get('clave', item.get('codigo')): item for item in raw_impacto if isinstance(item, dict)}
            except Exception as e:
                logger.warning("Error parseando impacto_variables: %s", e)

        for meta in VARIABLES_FINANCIERAS:
            cod = meta['codigo']
            clave = meta['clave']
            extra = METADATA_ADICIONAL_RATIOS.get(cod, {})

            item = shap_dict.get(clave) or shap_dict.get(cod)
            if not item:
                for v in shap_dict.values():
                    if isinstance(v, dict) and (v.get('codigo') == cod or v.get('clave') == clave):
                        item = v
                        break

            if item and isinstance(item, dict):
                item_copy = dict(item)
                item_copy['formula'] = extra.get('formula', '')
                item_copy['meta'] = extra.get('meta', '')
                item_copy['es_top_3'] = any(t.get('codigo') == cod for t in top_3_variables)
                todos_los_ratios_prediccion.append(item_copy)
            else:
                val = getattr(ratio_asociado_prediccion, meta['clave_etl'], None) if ratio_asociado_prediccion else None
                val_float = float(val) if val is not None else 0.0
                texto_desc = meta.get('desc_alza', '') if val_float > 0 else meta.get('desc_baja', '')
                if not texto_desc:
                    texto_desc = f"{meta['nombre']}: {val_float:.2f}{meta['unidad']}"

                todos_los_ratios_prediccion.append({
                    'codigo': cod,
                    'clave': clave,
                    'nombre': meta['nombre'],
                    'grupo': meta['grupo'],
                    'valor': val_float,
                    'unidad': meta['unidad'],
                    'impacto_shap': 0.0,
                    'impacto_pct': 0.0,
                    'impacto_abs': 0.0,
                    'texto': texto_desc,
                    'texto_resumen': f"Ratio {meta['nombre']}",
                    'aumenta_riesgo': False,
                    'formula': extra.get('formula', ''),
                    'meta': extra.get('meta', ''),
                    'es_top_3': any(t.get('codigo') == cod for t in top_3_variables),
                })

        # Información de los estados financieros del período asociado (Activo, Pasivo, Patrimonio, etc.)
        carga_financiera = None
        if ratio_asociado_prediccion and ratio_asociado_prediccion.carga:
            carga_financiera = ratio_asociado_prediccion.carga
        elif ratio_asociado_prediccion and ratio_asociado_prediccion.periodo:
            carga_qs = CargaFinanciera.objects.filter(periodo=ratio_asociado_prediccion.periodo)
            if empresa_usuario:
                carga_qs = carga_qs.filter(empresa=empresa_usuario)
            carga_financiera = carga_qs.order_by('-fecha_carga', '-id').first()

        if not carga_financiera and empresa_usuario:
            carga_financiera = CargaFinanciera.objects.filter(empresa=empresa_usuario).order_by('-fecha_carga', '-id').first()

        info_periodo = None
        if carga_financiera:
            act_total = float(carga_financiera.activo_total or 0)
            pas_total = float(carga_financiera.pasivo_total or 0)
            patrimonio = float(carga_financiera.patrimonio or 0)
            act_cte = float(carga_financiera.activo_corriente or 0)
            pas_cte = float(carga_financiera.pasivo_corriente or 0)
            act_no_cte = max(0.0, act_total - act_cte)
            pas_no_cte = max(0.0, pas_total - pas_cte)
            cap_trabajo = act_cte - pas_cte
            ingresos = float(carga_financiera.ingresos_netos or 0)
            ebit = float(carga_financiera.ebit or 0)
            util_neta = float(carga_financiera.utilidad_neta or 0)
            efectivo = float(carga_financiera.efectivo_equivalentes or 0)
            inventarios = float(carga_financiera.inventarios or 0)
            util_retenidas = float(carga_financiera.utilidades_retenidas or 0)

            dif_cuadre = abs(act_total - (pas_total + patrimonio))
            cuadrado = dif_cuadre < 2.0

            info_periodo = {
                'periodo': carga_financiera.periodo,
                'fecha_carga': carga_financiera.fecha_carga,
                'archivo_origen': carga_financiera.archivo_origen,
                'tipo_carga': carga_financiera.tipo_carga,
                'activo_total': act_total,
                'pasivo_total': pas_total,
                'patrimonio': patrimonio,
                'activo_corriente': act_cte,
                'pasivo_corriente': pas_cte,
                'activo_no_corriente': act_no_cte,
                'pasivo_no_corriente': pas_no_cte,
                'capital_trabajo': cap_trabajo,
                'ingresos_netos': ingresos,
                'ebit': ebit,
                'utilidad_neta': util_neta,
                'efectivo_equivalentes': efectivo,
                'inventarios': inventarios,
                'utilidades_retenidas': util_retenidas,
                'cuadrado': cuadrado,
                'dif_cuadre': dif_cuadre,
                'ratio_endeudamiento': (pas_total / act_total * 100.0) if act_total else 0.0,
                'margen_ebit_pct': (ebit / ingresos * 100.0) if ingresos else 0.0,
                'margen_neto_pct': (util_neta / ingresos * 100.0) if ingresos else 0.0,
            }

        # 5. Definición de variables de período, filtros y comprobación de datos existentes
        periodo_activo = ''
        if ultima_prediccion and ultima_prediccion.ratio and ultima_prediccion.ratio.periodo:
            periodo_activo = ultima_prediccion.ratio.periodo
        elif ultimo_ratio and ultimo_ratio.periodo:
            periodo_activo = ultimo_ratio.periodo
        elif carga_financiera and carga_financiera.periodo:
            periodo_activo = carga_financiera.periodo

        periodo_filtro = periodo_param or periodo_activo
        rango_filtro = (self.request.GET.get('rango') or '').strip()
        tiene_datos = bool(ultima_prediccion or ultimo_ratio or carga_financiera)

        # Entrega de datos al contexto (incluyendo JSON serializado seguro para Chart.js y UI)
        context.update({
            'empresa_usuario': empresa_usuario,
            'usuario_rol': self.get_user_role(),
            'tiene_datos': tiene_datos,
            'ultima_prediccion': ultima_prediccion,
            'score': score,
            'nivel': nivel,
            'fecha_prediccion': fecha_prediccion,
            'top_3_variables': top_3_variables,
            'todos_los_ratios_prediccion': todos_los_ratios_prediccion,
            'ratio_asociado_prediccion': ratio_asociado_prediccion,
            'carga_financiera': carga_financiera,
            'info_periodo': info_periodo,
            'es_prediccion_mas_reciente': es_prediccion_mas_reciente,
            'prediccion_id_seleccionada': ultima_prediccion.id if ultima_prediccion else None,
            'ingreso_real_hoy': ingreso_real_hoy,
            'total_ventas_hoy': total_ventas_hoy,
            'ultimo_ratio': ultimo_ratio,
            'total_predicciones_historicas': predicciones_qs.count(),
            # Detección de outliers (RF-10)
            'anomalias_detectadas': anomalias_detectadas,
            'tiene_anomalias': tiene_anomalias,
            'total_anomalias': len(anomalias_detectadas),
            'anomalias_json': json.dumps(anomalias_detectadas, ensure_ascii=False),
            # JSON seguro para el frontend y control interactivo (RF-04)
            'periodos_disponibles': periodos_disponibles,
            'periodos_disponibles_json': json.dumps(periodos_disponibles, ensure_ascii=False),
            'periodo_filtro': periodo_filtro,
            'rango_filtro': rango_filtro,
            'chart_fechas_json': json.dumps(chart_fechas, ensure_ascii=False),
            'chart_scores_json': json.dumps(chart_scores),
            'chart_niveles_json': json.dumps(chart_niveles),
            'chart_es_actual_json': json.dumps(chart_es_actual),
            'chart_puntos_json': json.dumps(chart_puntos, ensure_ascii=False),
            'top_3_shap_json': json.dumps(top_3_variables, ensure_ascii=False),
        })

        return context


class GenerarPDFView(DashboardRolMixin, View):
    """
    Controlador para exportar el Informe Ejecutivo en PDF utilizando ReportLab.
    Permite a los directivos descargar el diagnóstico formal estructurado de riesgo,
    explicabilidad SHAP completa, ratios financieros y estados contables.
    """

    def get(self, request: HttpRequest):
        usuario_db = resolver_usuario_bd(request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        predicciones_qs = PrediccionRiesgo.objects.select_related('empresa', 'ratio', 'ejecutada_por_usuario')
        if empresa_usuario:
            predicciones_qs = predicciones_qs.filter(empresa=empresa_usuario)
        elif not request.user.is_superuser:
            predicciones_qs = predicciones_qs.none()

        prediccion_id_param = (request.GET.get('prediccion_id') or '').strip()
        periodo_param = (request.GET.get('periodo') or '').strip()

        ultima_prediccion = None
        if prediccion_id_param and prediccion_id_param.isdigit():
            ultima_prediccion = predicciones_qs.filter(id=int(prediccion_id_param)).first()
        if not ultima_prediccion and periodo_param:
            ultima_prediccion = predicciones_qs.filter(
                Q(ratio__periodo=periodo_param) | Q(ratio__periodo__icontains=periodo_param)
            ).order_by('-fecha_prediccion', '-id').first()
        if not ultima_prediccion:
            ultima_prediccion = predicciones_qs.order_by('-fecha_prediccion', '-id').first()

        # Variables influyentes SHAP
        top_3_variables = []
        if ultima_prediccion and ultima_prediccion.variables_influyentes:
            try:
                top_3_variables = json.loads(ultima_prediccion.variables_influyentes)
            except Exception:
                top_3_variables = []

        # Ratios de la predicción activa (X1 a X7, Z Altman, Prueba Ácida)
        ratios_qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
        elif not request.user.is_superuser:
            ratios_qs = ratios_qs.none()

        ultimo_ratio = (
            ultima_prediccion.ratio
            if (ultima_prediccion and ultima_prediccion.ratio)
            else ratios_qs.order_by('-fecha_calculo', '-id').first()
        )
        ratio_asociado_prediccion = ultimo_ratio

        METADATA_ADICIONAL_RATIOS = {
            'X1': {'formula': 'Activo Corriente / Pasivo Corriente', 'meta': '> 1.50x'},
            'X2': {'formula': 'Capital de Trabajo / Activo Total', 'meta': '> 0.0%'},
            'X3': {'formula': 'Pasivo Total / Patrimonio Neto', 'meta': '< 1.00x'},
            'X4': {'formula': 'Utilidad Operacional / Activo Total', 'meta': '> 5.0%'},
            'X5': {'formula': 'Utilidad Operacional / Ventas Netas', 'meta': '> 10.0%'},
            'X6': {'formula': 'Ventas Netas / Activo Total', 'meta': '> 1.00x'},
            'X7': {'formula': 'Desviación Flujo Diario / Flujo Medio', 'meta': 'Baja dispersión'},
        }

        shap_dict = {}
        if ultima_prediccion and ultima_prediccion.impacto_variables:
            try:
                raw_impacto = json.loads(ultima_prediccion.impacto_variables)
                if isinstance(raw_impacto, dict):
                    shap_dict = raw_impacto
                elif isinstance(raw_impacto, list):
                    shap_dict = {item.get('clave', item.get('codigo')): item for item in raw_impacto if isinstance(item, dict)}
            except Exception as e:
                logger.warning("Error parseando impacto_variables: %s", e)

        todos_los_ratios_prediccion = []
        for meta in VARIABLES_FINANCIERAS:
            cod = meta['codigo']
            clave = meta['clave']
            extra = METADATA_ADICIONAL_RATIOS.get(cod, {})

            item = shap_dict.get(clave) or shap_dict.get(cod)
            if not item:
                for v in shap_dict.values():
                    if isinstance(v, dict) and (v.get('codigo') == cod or v.get('clave') == clave):
                        item = v
                        break

            if item and isinstance(item, dict):
                item_copy = dict(item)
                item_copy['formula'] = extra.get('formula', '')
                item_copy['meta'] = extra.get('meta', '')
                item_copy['es_top_3'] = any(t.get('codigo') == cod for t in top_3_variables)
                todos_los_ratios_prediccion.append(item_copy)
            else:
                val = getattr(ratio_asociado_prediccion, meta['clave_etl'], None) if ratio_asociado_prediccion else None
                val_float = float(val) if val is not None else 0.0
                texto_desc = meta.get('desc_alza', '') if val_float > 0 else meta.get('desc_baja', '')
                if not texto_desc:
                    texto_desc = f"{meta['nombre']}: {val_float:.2f}{meta['unidad']}"

                todos_los_ratios_prediccion.append({
                    'codigo': cod,
                    'clave': clave,
                    'nombre': meta['nombre'],
                    'grupo': meta['grupo'],
                    'valor': val_float,
                    'unidad': meta['unidad'],
                    'impacto_shap': 0.0,
                    'impacto_pct': 0.0,
                    'impacto_abs': 0.0,
                    'texto': texto_desc,
                    'texto_resumen': f"Ratio {meta['nombre']}",
                    'aumenta_riesgo': False,
                    'formula': extra.get('formula', ''),
                    'meta': extra.get('meta', ''),
                    'es_top_3': any(t.get('codigo') == cod for t in top_3_variables),
                })

        # Información del balance contable del período
        carga_financiera = None
        if ratio_asociado_prediccion and ratio_asociado_prediccion.carga:
            carga_financiera = ratio_asociado_prediccion.carga
        elif ratio_asociado_prediccion and ratio_asociado_prediccion.periodo:
            carga_qs = CargaFinanciera.objects.filter(periodo=ratio_asociado_prediccion.periodo)
            if empresa_usuario:
                carga_qs = carga_qs.filter(empresa=empresa_usuario)
            carga_financiera = carga_qs.order_by('-fecha_carga', '-id').first()

        if not carga_financiera and empresa_usuario:
            carga_financiera = CargaFinanciera.objects.filter(empresa=empresa_usuario).order_by('-fecha_carga', '-id').first()

        info_periodo = None
        if carga_financiera:
            act_total = float(carga_financiera.activo_total or 0)
            pas_total = float(carga_financiera.pasivo_total or 0)
            patrimonio = float(carga_financiera.patrimonio or 0)
            act_cte = float(carga_financiera.activo_corriente or 0)
            pas_cte = float(carga_financiera.pasivo_corriente or 0)
            act_no_cte = max(0.0, act_total - act_cte)
            pas_no_cte = max(0.0, pas_total - pas_cte)
            cap_trabajo = act_cte - pas_cte
            ingresos = float(carga_financiera.ingresos_netos or 0)
            ebit = float(carga_financiera.ebit or 0)
            util_neta = float(carga_financiera.utilidad_neta or 0)
            efectivo = float(carga_financiera.efectivo_equivalentes or 0)
            inventarios = float(carga_financiera.inventarios or 0)
            util_retenidas = float(carga_financiera.utilidades_retenidas or 0)

            dif_cuadre = abs(act_total - (pas_total + patrimonio))
            cuadrado = dif_cuadre < 2.0

            info_periodo = {
                'periodo': carga_financiera.periodo,
                'fecha_carga': carga_financiera.fecha_carga,
                'archivo_origen': carga_financiera.archivo_origen,
                'tipo_carga': carga_financiera.tipo_carga,
                'activo_total': act_total,
                'pasivo_total': pas_total,
                'patrimonio': patrimonio,
                'activo_corriente': act_cte,
                'pasivo_corriente': pas_cte,
                'activo_no_corriente': act_no_cte,
                'pasivo_no_corriente': pas_no_cte,
                'capital_trabajo': cap_trabajo,
                'ingresos_netos': ingresos,
                'ebit': ebit,
                'utilidad_neta': util_neta,
                'efectivo_equivalentes': efectivo,
                'inventarios': inventarios,
                'utilidades_retenidas': util_retenidas,
                'cuadrado': cuadrado,
                'dif_cuadre': dif_cuadre,
                'ratio_endeudamiento': (pas_total / act_total * 100.0) if act_total else 0.0,
                'margen_ebit_pct': (ebit / ingresos * 100.0) if ingresos else 0.0,
                'margen_neto_pct': (util_neta / ingresos * 100.0) if ingresos else 0.0,
            }

        # Evaluaciones históricas (para mostrar la curva / tendencia de solvencia en tabla)
        ultimas_predicciones = list(predicciones_qs.order_by('-fecha_prediccion', '-id')[:10])
        predicciones_cronologicas = list(reversed(ultimas_predicciones))
        historico_puntos = [
            {
                'id': p.id,
                'periodo': p.ratio.periodo if (p.ratio and p.ratio.periodo) else (p.fecha_prediccion.strftime('%d/%m/%Y') if p.fecha_prediccion else f"#{p.id}"),
                'fecha': p.fecha_prediccion.strftime('%d/%m/%Y %H:%M') if p.fecha_prediccion else 'N/A',
                'score': float(p.score_riesgo or 0.0),
                'nivel': p.nivel_semaforo or ('Rojo' if (p.score_riesgo or 0) > 70 else 'Amarillo' if (p.score_riesgo or 0) > 35 else 'Verde'),
                'es_actual': bool(ultima_prediccion and p.id == ultima_prediccion.id),
            }
            for p in predicciones_cronologicas
        ]

        # Operaciones de caja y ventas de hoy
        hoy = timezone.localdate()
        ventas_hoy_qs = Venta.objects.filter(fecha__date=hoy)
        if empresa_usuario:
            ventas_hoy_qs = ventas_hoy_qs.filter(empresa=empresa_usuario)
        elif not request.user.is_superuser:
            ventas_hoy_qs = ventas_hoy_qs.none()

        ingreso_real_hoy = ventas_hoy_qs.aggregate(total=Sum('ingreso_real'))['total'] or Decimal('0.00')
        total_ventas_hoy = ventas_hoy_qs.count()

        try:
            pdf_buffer = construir_informe_ejecutivo_pdf(
                empresa=empresa_usuario,
                ultima_prediccion=ultima_prediccion,
                top_3_variables=top_3_variables,
                ingreso_real_hoy=ingreso_real_hoy,
                usuario=usuario_db or request.user,
                total_ventas_hoy=total_ventas_hoy,
                todos_los_ratios=todos_los_ratios_prediccion,
                ratio_asociado=ratio_asociado_prediccion,
                info_periodo=info_periodo,
                historico_puntos=historico_puntos,
            )

            per_slug = ""
            if ultima_prediccion and ultima_prediccion.ratio and ultima_prediccion.ratio.periodo:
                per_slug = f"_{ultima_prediccion.ratio.periodo}"
            nombre_archivo = f"informe_ejecutivo_riesgo{per_slug}_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
        except Exception as exc:
            logger.exception("Error al compilar el informe ejecutivo PDF: %s", exc)
            messages.error(
                request,
                "No fue posible generar el informe ejecutivo en este momento debido a un problema temporal. "
                "Por favor, reintente la descarga o contacte al soporte del sistema."
            )
            return redirect('dashboard:dashboard')


class EjecutarPrediccionDashboardView(DashboardRolMixin, View):
    """
    Acción rápida para invocar el MotorRiesgo desde el Dashboard
    sobre el último RatioFinanciero disponible.
    """

    def post(self, request: HttpRequest):
        usuario_db = resolver_usuario_bd(request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        ratios_qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
        elif not request.user.is_superuser:
            ratios_qs = ratios_qs.none()

        ratio_id = request.POST.get('ratio_id')
        if ratio_id:
            ratio_a_ejecutar = ratios_qs.filter(id=ratio_id).first()
            if not ratio_a_ejecutar:
                messages.error(
                    request,
                    "El período o ratio contable seleccionado no existe o no pertenece a su empresa."
                )
                return redirect('dashboard:dashboard')
        else:
            ratio_a_ejecutar = ratios_qs.order_by('-fecha_calculo', '-id').first()

        if not ratio_a_ejecutar:
            messages.warning(
                request,
                "No se encontraron ratios financieros cargados para esta empresa. Cargue un balance en el Módulo ETL primero."
            )
            return redirect('dashboard:dashboard')

        # Detección de valores anómalos (outliers) previa a la ejecución (RF-10)
        anomalias = detectar_anomalias_financieras(ratio_a_ejecutar)
        forzar_ejecucion = request.POST.get('forzar_ejecucion') in ('1', 'true', 'True')

        if anomalias and not forzar_ejecucion:
            messages.warning(
                request,
                f"Advertencia [RF-10]: Se detectaron {len(anomalias)} valores anómalos o fuera de rango (outliers). "
                "Para proteger la calidad predictiva, confirme la advertencia en el modal de confirmación o corrija los datos."
            )
            return redirect('dashboard:dashboard')

        try:
            prediccion, resultado = ejecutar_y_persistir_prediccion(
                ratio_obj_o_id=ratio_a_ejecutar,
                usuario=usuario_db,
                empresa=empresa_usuario
            )
            periodo_txt = f" para el período '{ratio_a_ejecutar.periodo}'" if ratio_a_ejecutar.periodo else ""
            msg_exito = f"¡Ejecución de Análisis completada exitosamente{periodo_txt}! Score: {resultado['score']}% - Nivel: {resultado['nivel']}."
            if anomalias and forzar_ejecucion:
                msg_exito += f" (Se forzó la ejecución aceptando {len(anomalias)} valor(es) anómalo(s) / outlier(s) detectados)."
            messages.success(request, msg_exito)
        except Exception as exc:
            logger.exception("Error al ejecutar predicción ML desde el dashboard: %s", exc)
            messages.error(
                request,
                "No fue posible completar la evaluación del modelo analítico en este momento por una interrupción del servicio. "
                "Por favor, reintente la operación en unos instantes."
            )

        return redirect('dashboard:dashboard')
