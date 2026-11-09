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
from django.http import HttpResponse, HttpRequest, Http404, JsonResponse
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
from AppWeb.viewsML import calcular_periodo_siguiente, calcular_delta_riesgo
from .pdf_generator import construir_informe_ejecutivo_pdf

logger = logging.getLogger(__name__)


def calcular_z_score_altman_1983(r_obj) -> float:
    """
    Formulación clásica de Edward Altman (1983) para empresas no manufactureras
    y mercados emergentes (Z''-Score):
    Z'' = 6.56 * X1 + 3.26 * X2 + 6.72 * X3 + 1.05 * X4

    Donde:
      X1 = (Activo Circulante - Pasivo Circulante) / Activo Total  (Capital de Trabajo / Activo Total)
      X2 = Utilidades Retenidas / Activo Total
      X3 = EBIT / Activo Total  (Rentabilidad Operacional del Activo / ROA Operacional)
      X4 = Patrimonio Neto / Pasivo Total  (Valor Contable del Patrimonio / Pasivo Total = 1 / Leverage)
    """
    if not r_obj:
        return 2.60

    carga = getattr(r_obj, 'carga', None)
    if carga and carga.activo_total and float(carga.activo_total) > 0:
        at = float(carga.activo_total)
        ac = float(carga.activo_corriente or 0.0)
        pc = float(carga.pasivo_corriente or 0.0)
        pt = float(carga.pasivo_total or 0.0)
        pat = float(carga.patrimonio or 0.0)
        ur = float(carga.utilidades_retenidas or 0.0)
        ebit = float(carga.ebit or 0.0)

        x1 = (ac - pc) / at
        x2 = ur / at
        x3 = ebit / at
        x4 = (pat / pt) if pt > 0 else 10.0
    else:
        # Extraer desde los ratios financieros almacenados en r_obj
        x1 = float(getattr(r_obj, 'v2_capital_trabajo_activos', None) or 0.1)
        x3 = float(getattr(r_obj, 'v4_roa_operacional', None) or 0.04)
        lev = float(getattr(r_obj, 'v3_leverage_total', None) or 1.5)
        x4 = (1.0 / lev) if lev > 0 else 10.0

        if getattr(r_obj, 'ref_z_altman', None) is not None:
            # En moduloETL se calcula con la constante EMS (3.25 + 6.56*X1 + 3.26*X2 + ...)
            val_ref = float(r_obj.ref_z_altman)
            return round(val_ref - 3.25, 4)
        x2 = x3 * 0.5

    z_double_prime = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
    return round(z_double_prime, 4)


def calcular_score_observado(r_obj) -> float:
    """
    Calcula el puntaje de insolvencia contable observado (0 a 100%) a partir de la
    formulación clásica de Edward Altman (1983) para empresas no manufactureras
    y mercados emergentes (Z''-Score).

    Mapeo de Zonas Canónicas de Altman (1983) al Semáforo Gerencial:
      - Z'' >= 2.60 : Zona Segura / Solvente      -> Score <= 35.0% (Verde)
      - 1.10 <= Z'' < 2.60 : Zona Gris / Alerta   -> Score 35.0% a 70.0% (Amarillo)
      - Z'' < 1.10  : Zona de Quiebra / Distress  -> Score > 70.0% (Rojo)
    """
    if not r_obj:
        return 35.0

    z_score = calcular_z_score_altman_1983(r_obj)

    if z_score >= 2.60:
        # Zona Segura: puntuación entre 5% y 35% (a mayor Z'', menor riesgo de quiebra)
        score = 35.0 - (z_score - 2.60) * 10.0
    elif z_score >= 1.10:
        # Zona Gris: interpolación lineal exacta entre 35% (Z=2.60) y 70% (Z=1.10)
        score = 35.0 + (2.60 - z_score) * (35.0 / 1.50)
    else:
        # Zona de Quiebra (Distress): puntuación entre 70% y 95% (a menor Z'', mayor riesgo)
        score = 70.0 + (1.10 - z_score) * 20.0

    return round(float(max(5.0, min(95.0, score))), 1)



def resolver_usuario_bd(auth_user):
    """
    Obtiene la entidad Usuario del sistema a partir del usuario Django en sesión con caché en memoria.
    """
    if not auth_user:
        return None
    if isinstance(auth_user, Usuario):
        return auth_user
    if not getattr(auth_user, 'is_authenticated', False):
        return None
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
        if not user or not getattr(user, 'is_authenticated', True):
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
        if getattr(self.request.user, 'is_superuser', False):
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
    Soporta peticiones síncronas estándar y asíncronas (AJAX / Fetch)
    para actualizar datos de forma reactiva e instantánea sin recargar la página.
    """
    template_name = 'dashboard/dashboard.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
            context = self.get_context_data(**kwargs)
            ultima = context.get('ultima_prediccion')
            info_p = context.get('info_periodo')
            if info_p:
                info_p = dict(info_p)
                if info_p.get('fecha_carga'):
                    fc = info_p['fecha_carga']
                    info_p['fecha_carga'] = fc.strftime('%d/%m/%Y %H:%M') if hasattr(fc, 'strftime') else str(fc)

            fecha_pred = context.get('fecha_prediccion')
            fecha_pred_str = fecha_pred.strftime('%d/%m/%Y %H:%M') if (fecha_pred and hasattr(fecha_pred, 'strftime')) else 'Pendiente'

            ratio_obj = context.get('ratio_asociado_prediccion')
            ratio_per = ratio_obj.periodo if ratio_obj else context.get('periodo_filtro')

            data = {
                'status': 'ok',
                'prediccion_id': ultima.id if ultima else None,
                'periodo': context.get('periodo_filtro') or (ultima.ratio.periodo if (ultima and ultima.ratio) else ''),
                'score': context.get('score'),
                'nivel': context.get('nivel'),
                'fecha_prediccion': fecha_pred_str,
                'es_prediccion_mas_reciente': context.get('es_prediccion_mas_reciente'),
                'top_3_variables': context.get('top_3_variables') or [],
                'todos_los_ratios_prediccion': context.get('todos_los_ratios_prediccion') or [],
                'info_periodo': info_p,
                'ratio_periodo': ratio_per,
            }
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

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
        # Ratios disponibles para identificar balance activo y asociar formulación de Altman (1983)
        ratios_qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            ratios_qs = ratios_qs.none()

        # Extraer todos los períodos históricos disponibles para los filtros
        periodos_disponibles = []
        for p in predicciones_qs:
            per = p.ratio.periodo if (p.ratio and p.ratio.periodo) else (p.fecha_prediccion.strftime('%d/%m/%Y') if p.fecha_prediccion else f"#{p.id}")
            if per and per not in periodos_disponibles:
                periodos_disponibles.append(per)
        for r in ratios_qs:
            if r.periodo and r.periodo not in periodos_disponibles:
                periodos_disponibles.append(r.periodo)
        periodos_disponibles.sort()

        # Hasta 20 evaluaciones históricas para graficación y filtrado dinámico (RF-04)
        predicciones_curva = predicciones_qs
        if periodo_param and not (self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.GET.get('ajax') == '1'):
            predicciones_curva = predicciones_curva.filter(
                Q(ratio__periodo=periodo_param) | Q(ratio__periodo__icontains=periodo_param)
            )
        ultimas_predicciones = list(predicciones_curva.order_by('-fecha_prediccion', '-id')[:20])
        # Invertir a orden cronológico ascendente para el eje horizontal del gráfico
        predicciones_cronologicas = list(reversed(ultimas_predicciones))

        chart_puntos = []
        periodos_pasados_labels = []
        valores_observados = []
        valores_predicciones = []

        for p in predicciones_cronologicas:
            per_raw = p.ratio.periodo if (p.ratio and p.ratio.periodo) else (p.fecha_prediccion.strftime('%d/%m/%Y') if p.fecha_prediccion else f"#{p.id}")
            p_fut, per_norm, _ = calcular_periodo_siguiente(per_raw)
            lbl_clean = per_norm or per_raw
            r_obj = p.ratio
            if not r_obj and per_raw:
                r_obj = ratios_qs.filter(periodo=per_raw).order_by('-id').first()

            if r_obj:
                sc_obs = calcular_score_observado(r_obj)
            else:
                sc_obs = float(p.score_riesgo or 35.0)

            sc_pred = float(p.score_riesgo or 0.0)
            niv_obs = 'Verde' if sc_obs <= 35 else ('Amarillo' if sc_obs <= 70 else 'Rojo')
            niv_pred = p.nivel_semaforo or ('Verde' if sc_pred <= 35 else ('Amarillo' if sc_pred <= 70 else 'Rojo'))
            es_act = bool(ultima_prediccion and p.id == ultima_prediccion.id)

            periodos_pasados_labels.append(lbl_clean)
            valores_observados.append(sc_obs)
            valores_predicciones.append(sc_pred)

            chart_puntos.append({
                'id': p.id,
                'periodo': per_raw,
                'label': lbl_clean,
                'fecha_corta': p.fecha_prediccion.strftime('%d/%m %H:%M') if p.fecha_prediccion else '',
                'fecha_completa': p.fecha_prediccion.strftime('%d/%m/%Y %H:%M') if p.fecha_prediccion else '',
                'score_observado': sc_obs,
                'score_prediccion': sc_pred,
                'score': sc_pred,
                'nivel': niv_pred,
                'nivel_observado': niv_obs,
                'periodo_proyectado': p_fut,
                'score_proyectado': sc_pred,
                'es_actual': es_act,
            })

        if ultima_prediccion and chart_puntos and not any(pt['es_actual'] for pt in chart_puntos):
            chart_puntos[-1]['es_actual'] = True

        chart_scores = [pt['score'] for pt in chart_puntos]
        chart_fechas = [pt['label'] for pt in chart_puntos]
        chart_niveles = [pt['nivel'] for pt in chart_puntos]
        chart_es_actual = [pt['es_actual'] for pt in chart_puntos]

        ultimo_ratio = (
            ultima_prediccion.ratio
            if (ultima_prediccion and ultima_prediccion.ratio)
            else ratios_qs.order_by('-fecha_calculo', '-id').first()
        )

        # Proyección futura a 90 días (Q_{t+1}) para la curva de tendencia con alternador/ocultador
        periodo_base_dashboard = ''
        if ultima_prediccion and ultima_prediccion.ratio and ultima_prediccion.ratio.periodo:
            periodo_base_dashboard = ultima_prediccion.ratio.periodo
        elif ultimo_ratio and ultimo_ratio.periodo:
            periodo_base_dashboard = ultimo_ratio.periodo
        elif chart_puntos:
            periodo_base_dashboard = chart_puntos[-1]['periodo']
        else:
            periodo_base_dashboard = '2024-Q4'

        periodo_proyectado_dashboard, periodo_base_norm_dashboard, dias_horizonte_dashboard = calcular_periodo_siguiente(periodo_base_dashboard)
        score_proyectado_dashboard = float(score) if score is not None else 35.0
        nivel_proyectado_dashboard = nivel if (nivel and nivel != 'Sin Datos') else ('Verde' if score_proyectado_dashboard <= 35 else 'Amarillo' if score_proyectado_dashboard <= 70 else 'Rojo')

        idx_act = -1
        for idx_h, pt in enumerate(chart_puntos):
            if pt['es_actual']:
                idx_act = idx_h
                break
        if idx_act == -1 and chart_puntos:
            idx_act = len(chart_puntos) - 1

        punto_activo = chart_puntos[idx_act] if (0 <= idx_act < len(chart_puntos)) else None
        score_base_dashboard = punto_activo['score_observado'] if punto_activo else (float(score) if score is not None else 35.0)
        score_actual_proy = punto_activo['score_prediccion'] if punto_activo else score_proyectado_dashboard
        score_anterior_dashboard = valores_predicciones[idx_act - 1] if idx_act >= 1 else None
        delta_info_dashboard = calcular_delta_riesgo(score_actual_proy, score_anterior_dashboard)

        timeline_labels = list(periodos_pasados_labels) + [periodo_proyectado_dashboard]
        timeline_observado_data = list(valores_observados) + [None]
        timeline_predicciones_data = list(valores_predicciones) + [None]

        M = len(periodos_pasados_labels)
        timeline_proyectado_dashboard = [None] * len(timeline_labels)
        if M > 0:
            if idx_act == M - 1:
                timeline_proyectado_dashboard[idx_act] = score_base_dashboard
                timeline_proyectado_dashboard[M] = score_actual_proy
            else:
                timeline_proyectado_dashboard[idx_act] = score_base_dashboard
                timeline_proyectado_dashboard[idx_act + 1] = score_actual_proy
        elif score is not None:
            timeline_proyectado_dashboard = [score_proyectado_dashboard]

        # 4. Total Ingreso_Real del día actual sumando transacciones de Venta (moduloTransaccional / app_caja)
        hoy = timezone.localdate()
        ventas_hoy_qs = Venta.objects.filter(fecha__date=hoy)
        if empresa_usuario:
            ventas_hoy_qs = ventas_hoy_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            ventas_hoy_qs = ventas_hoy_qs.none()

        ingreso_real_hoy = ventas_hoy_qs.aggregate(total=Sum('ingreso_real'))['total'] or Decimal('0.00')
        total_ventas_hoy = ventas_hoy_qs.count()

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
            # Datos alineados para visualización idéntica y compatible con dashboard_predictivo
            'timeline_puntos': chart_puntos,
            'timeline_puntos_json': json.dumps(chart_puntos, ensure_ascii=False),
            'timeline_labels': timeline_labels,
            'timeline_labels_json': json.dumps(timeline_labels, ensure_ascii=False),
            'timeline_observado_json': json.dumps(timeline_observado_data),
            'timeline_predicciones_json': json.dumps(timeline_predicciones_data),
            'timeline_historico_json': json.dumps(timeline_observado_data),
            'valores_observados': valores_observados,
            'valores_predicciones': valores_predicciones,
            'etiquetas_periodos_pasados': periodos_pasados_labels,
            # Proyección a 90 días para el gráfico con alternador/ocultador
            'periodo_proyectado': periodo_proyectado_dashboard,
            'periodo_proyectado_json': json.dumps(periodo_proyectado_dashboard, ensure_ascii=False),
            'score_proyectado': score_proyectado_dashboard,
            'score_base_dashboard': score_base_dashboard,
            'nivel_proyectado': nivel_proyectado_dashboard,
            'delta_info': delta_info_dashboard,
            'timeline_proyectado_json': json.dumps(timeline_proyectado_dashboard),
        })

        return context


class DashboardPredictivoView(DashboardView):
    """
    Controlador de la Interfaz de Resultados Predictivos y Alerta Temprana a 3 Meses (Q_t -> Q_{t+1}).
    Transforma el diagnóstico estático a una herramienta proactiva de proyección financiera a 90 días.
    """
    template_name = 'dashboard/dashboard_predictivo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ultima_prediccion = context.get('ultima_prediccion')
        ultimo_ratio = context.get('ultimo_ratio')
        score = context.get('score')
        nivel = context.get('nivel') or 'Sin Datos'
        empresa_usuario = context.get('empresa_usuario')
        user = self.request.user

        # 1. Determinación de Q_t (período del balance analizado)
        periodo_param = (self.request.GET.get('periodo') or '').strip()
        periodo_balance_raw = ''
        if periodo_param:
            periodo_balance_raw = periodo_param
        elif ultima_prediccion and ultima_prediccion.ratio and ultima_prediccion.ratio.periodo:
            periodo_balance_raw = ultima_prediccion.ratio.periodo
        elif ultimo_ratio and ultimo_ratio.periodo:
            periodo_balance_raw = ultimo_ratio.periodo
        elif context.get('info_periodo') and context['info_periodo'].get('periodo'):
            periodo_balance_raw = context['info_periodo']['periodo']
        else:
            periodo_balance_raw = '2024-Q4'

        # 2. Cálculo dinámico de Q_{t+1} (período futuro proyectado a 90 días)
        periodo_proyectado, periodo_balance_norm, dias_horizonte = calcular_periodo_siguiente(periodo_balance_raw)

        # 3. Consulta optimizada de períodos, ratios y predicciones (evita iterar 15.000+ registros)
        ratios_qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            ratios_qs = ratios_qs.none()

        periodos_unicos = list(
            ratios_qs.exclude(periodo__isnull=True)
                     .exclude(periodo='')
                     .values_list('periodo', flat=True)
                     .distinct()
        )

        ratios_por_periodo = {}
        for per in periodos_unicos:
            r = ratios_qs.filter(periodo=per).order_by('-id').first()
            if r:
                ratios_por_periodo[per] = r

        predicciones_qs = PrediccionRiesgo.objects.select_related('ratio', 'empresa')
        if empresa_usuario:
            predicciones_qs = predicciones_qs.filter(empresa=empresa_usuario)
        elif not user.is_superuser:
            predicciones_qs = predicciones_qs.none()

        pred_por_periodo = {}
        for p in predicciones_qs.order_by('-fecha_prediccion', '-id'):
            if p.ratio and p.ratio.periodo and p.ratio.periodo not in pred_por_periodo:
                pred_por_periodo[p.ratio.periodo] = p

        from AppWeb.viewsML import predecir_riesgo

        # Identificar secuencia cronológica de trimestres válidos
        todos_periodos = sorted(ratios_por_periodo.keys())
        periodos_trimestrales = [p for p in todos_periodos if 'Q' in p or 'q' in p] or todos_periodos

        # IMPORTANTE: Preservar todos los trimestres disponibles sin recortar con [:idx_balance + 1]
        # para que el frontend disponga de la historia completa y el botón 'Todos' pueda restablecerla.
        periodos_visibles = list(periodos_trimestrales)

        timeline_puntos = []
        periodos_pasados_labels = []
        valores_observados = []
        valores_predicciones = []

        for per in periodos_visibles:
            p_fut, per_norm, _ = calcular_periodo_siguiente(per)
            r_obj = ratios_por_periodo[per]
            p_obj = pred_por_periodo.get(per)
            if p_obj and p_obj.score_riesgo is not None:
                sc_pred = float(p_obj.score_riesgo)
                niv_pred = p_obj.nivel_semaforo or ('Verde' if sc_pred <= 35 else 'Amarillo' if sc_pred <= 70 else 'Rojo')
                pid = p_obj.id
            else:
                vars_dict = {
                    'razon_corriente': float(r_obj.v1_razon_corriente or 1.0),
                    'capital_trabajo_sobre_activos': float(r_obj.v2_capital_trabajo_activos or 0.1),
                    'leverage_total': float(r_obj.v3_leverage_total or 1.0),
                    'roa_operacional': float(r_obj.v4_roa_operacional or 0.05),
                    'margen_operacional': float(r_obj.v5_margen_operacional or 0.08),
                    'rotacion_activos': float(r_obj.v6_rotacion_activos or 1.0),
                    'volatilidad_flujo_caja': float(r_obj.v7_volatilidad_flujo or 0.5),
                }
                sc_pred, niv_pred, _ = predecir_riesgo(vars_dict)
                pid = None

            sc_obs = calcular_score_observado(r_obj)
            niv_obs = 'Verde' if sc_obs <= 35 else ('Amarillo' if sc_obs <= 70 else 'Rojo')

            lbl_clean = per_norm or per
            es_act = bool(per == periodo_balance_raw or per == periodo_balance_norm or per_norm == periodo_balance_norm)
            periodos_pasados_labels.append(lbl_clean)
            valores_observados.append(sc_obs)
            valores_predicciones.append(sc_pred)

            timeline_puntos.append({
                'id': pid,
                'periodo': per,
                'label': lbl_clean,
                'score_observado': sc_obs,
                'score_prediccion': sc_pred,
                'score': sc_pred,
                'nivel': niv_pred,
                'nivel_observado': niv_obs,
                'periodo_proyectado': p_fut,
                'score_proyectado': sc_pred,
                'es_actual': es_act,
            })

        if not periodos_pasados_labels:
            score_actual = float(score) if score is not None else 0.0
            periodos_pasados_labels = [periodo_balance_norm]
            valores_observados = [score_actual]
            valores_predicciones = [score_actual]
            valores_historicos = [score_actual]
            timeline_puntos = [{
                'id': ultima_prediccion.id if ultima_prediccion else None,
                'periodo': periodo_balance_norm,
                'label': periodo_balance_norm,
                'score_observado': score_actual,
                'score_prediccion': score_actual,
                'score': score_actual,
                'nivel': nivel,
                'nivel_observado': nivel,
                'periodo_proyectado': periodo_proyectado,
                'score_proyectado': score_actual,
                'es_actual': True,
            }]
            score_anterior = None
            score_base_qt = score_actual
            delta_info = calcular_delta_riesgo(score_actual, score_anterior)

            timeline_labels = list(periodos_pasados_labels) + [periodo_proyectado]
            timeline_observado_data = list(valores_observados) + [None]
            timeline_predicciones_data = list(valores_predicciones) + [None]
            timeline_historico_data = list(valores_observados) + [None]
            timeline_proyectado_data = [score_base_qt, score_actual]
        else:
            if not any(p['es_actual'] for p in timeline_puntos):
                timeline_puntos[-1]['es_actual'] = True

            # Encontrar índice del período activo para la proyección
            idx_act = -1
            for idx_h, p_item in enumerate(timeline_puntos):
                if p_item['es_actual']:
                    idx_act = idx_h
                    break
            if idx_act == -1:
                idx_act = len(timeline_puntos) - 1

            punto_activo = timeline_puntos[idx_act]
            score_actual = punto_activo['score_prediccion']
            score_base_qt = punto_activo['score_observado']

            if idx_act >= 1:
                score_anterior = valores_predicciones[idx_act - 1]
            else:
                score_anterior = None
            delta_info = calcular_delta_riesgo(score_actual, score_anterior)

            valores_historicos = list(valores_observados)

            # 4. Listas separadas de datos para el Gráfico Temporal con Proyección Futura (Chart.js)
            timeline_labels = list(periodos_pasados_labels) + [periodo_proyectado]
            timeline_observado_data = list(valores_observados) + [None]
            timeline_predicciones_data = list(valores_predicciones) + [None]
            timeline_historico_data = list(valores_observados) + [None]

            # Construir tramo proyectado según el período activo:
            # Si el activo es el último trimestre, conecta hacia periodo_proyectado (índice M).
            # Si el activo es un trimestre intermedio, conecta hacia el siguiente trimestre (índice idx_act + 1).
            M = len(periodos_pasados_labels)
            timeline_proyectado_data = [None] * len(timeline_labels)
            if idx_act == M - 1:
                timeline_proyectado_data[idx_act] = score_base_qt
                timeline_proyectado_data[M] = score_actual
            else:
                timeline_proyectado_data[idx_act] = score_base_qt
                timeline_proyectado_data[idx_act + 1] = score_actual

        # 5. Matriz de Validación Histórica (Backtesting Visual Retrospectivo) optimizada en O(1)
        matriz_backtesting = []
        lista_periodos_ordenados = sorted(ratios_por_periodo.keys())

        for idx_p, p_base in enumerate(lista_periodos_ordenados):
            p_fut, _, _ = calcular_periodo_siguiente(p_base)
            r_base = ratios_por_periodo[p_base]

            pred_asoc = pred_por_periodo.get(p_base)
            score_bt = float(pred_asoc.score_riesgo) if pred_asoc and pred_asoc.score_riesgo is not None else 35.0
            nivel_bt = pred_asoc.nivel_semaforo if pred_asoc else ('Verde' if score_bt <= 35 else 'Amarillo' if score_bt <= 70 else 'Rojo')
            color_bt = 'Verde' if (nivel_bt == 'Verde' or score_bt <= 35) else ('Amarillo' if score_bt <= 70 else 'Rojo')

            r_fut = ratios_por_periodo.get(p_fut)
            if r_fut:
                z_fut = calcular_z_score_altman_1983(r_fut)
                if z_fut >= 2.60:
                    estado_real = f"Solvente (Altman Z'': {z_fut:.2f})"
                    resultado_val = "Acierto Preventivo" if score_bt <= 35 else "Falsa Alarma Superada"
                    badge_val = "badge-status-solvente"
                elif z_fut < 1.10:
                    estado_real = f"Insolvente / Quiebra (Altman Z'': {z_fut:.2f})"
                    resultado_val = "Alerta Temprana Validada" if score_bt > 35 else "Insolvencia Sobrevenida"
                    badge_val = "badge-status-critico"
                else:
                    estado_real = f"Zona Gris / Tensión (Altman Z'': {z_fut:.2f})"
                    resultado_val = "Anticipación Correcta"
                    badge_val = "badge-status-alerta"
            else:
                if p_base == periodo_balance_raw or p_base == periodo_balance_norm:
                    estado_real = "Ventana Preventiva en Curso (90 días vigentes)"
                    resultado_val = "Pronóstico Activo"
                    badge_val = "badge-status-alerta"
                else:
                    estado_real = "Solvencia Preservada"
                    resultado_val = "Acierto Histórico"
                    badge_val = "badge-status-solvente"

            matriz_backtesting.append({
                'periodo_base': p_base,
                'periodo_proyectado': p_fut,
                'score_proyectado': score_bt,
                'nivel_proyectado': nivel_bt,
                'color_proyectado': color_bt,
                'estado_real': estado_real,
                'resultado': resultado_val,
                'badge_clase': badge_val,
                'es_activo': (p_base == periodo_balance_raw or p_base == periodo_balance_norm),
            })

        if not matriz_backtesting and score is not None:
            matriz_backtesting.append({
                'periodo_base': periodo_balance_norm,
                'periodo_proyectado': periodo_proyectado,
                'score_proyectado': score_actual,
                'nivel_proyectado': nivel,
                'color_proyectado': 'Verde' if nivel == 'Verde' else ('Amarillo' if nivel == 'Amarillo' else 'Rojo'),
                'estado_real': "Ventana Preventiva en Curso (90 días vigentes)",
                'resultado': "Pronóstico Activo",
                'badge_clase': "badge-status-alerta",
                'es_activo': True,
            })

        context.update({
            'periodo_balance': periodo_balance_norm,
            'periodo_balance_raw': periodo_balance_raw,
            'periodo_proyectado': periodo_proyectado,
            'ventana_preventiva_dias': dias_horizonte,
            'delta_info': delta_info,

            'etiquetas_periodos_pasados': periodos_pasados_labels,
            'valores_historicos': valores_historicos,
            'valores_observados': valores_observados,
            'valores_predicciones': valores_predicciones,
            'periodo_futuro_label': periodo_proyectado,
            'valor_proyectado': score_actual,
            'nivel_proyectado': nivel,

            'timeline_labels_json': json.dumps(timeline_labels, ensure_ascii=False),
            'timeline_observado_json': json.dumps(timeline_observado_data),
            'timeline_predicciones_json': json.dumps(timeline_predicciones_data),
            'timeline_historico_json': json.dumps(timeline_historico_data),
            'timeline_proyectado_json': json.dumps(timeline_proyectado_data),
            'timeline_puntos': timeline_puntos,
            'timeline_puntos_json': json.dumps(timeline_puntos, ensure_ascii=False),
            'total_evaluaciones_historicas': len(timeline_puntos),
            'score_proyectado_float': score_actual,

            'matriz_backtesting': matriz_backtesting,
            'total_trimestres_backtesting': len(matriz_backtesting),
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
