"""
Vistas del Módulo ETL (Extract, Transform, Load) de SmartFinanzas.
Implementa aislamiento por empresa (multi-tenant): los usuarios solo pueden ver
y gestionar información financiera perteneciente a su propia empresa.
"""

import os
import json
import logging
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Avg
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, FormView

from .models import CargaFinanciera, RatioFinanciero
from .forms import CargaArchivoForm
from .services import (
    procesar_e_ingestar_balance,
    limpiar_archivos_y_estado,
    generar_plantilla_ejemplo_csv,
    detectar_anomalias_financieras,
    COLUMNAS_PLANTILLA,
)
from usuarios.models import Usuario, Empresa
from AppWeb.models import EstadoCarga
from capaAnalitica.services import ejecutar_y_persistir_prediccion
from .etl_financiero import FinancialETLProcessor, ETLError

logger = logging.getLogger(__name__)


def resolver_usuario_bd(auth_user):
    """
    Obtiene la instancia de 'Usuario' (tabla usuario) correspondiente
    al usuario autenticado en la sesión de Django con caché en memoria.
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


class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin RBAC para restringir el acceso a usuarios con roles autorizados
    (Contador, Dueño, Administrador).
    """
    roles_permitidos = ['Contador', 'Dueño', 'Administrador']
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
        return None

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        rol = self.get_user_role()
        return rol in self.roles_permitidos


class CargaArchivoView(RolRequeridoMixin, View):
    """
    Vista principal de Ingesta y Carga de Archivos Contables (carga_datos.html).
    Impulsada por FinancialETLProcessor en memoria con soporte multi-formato (CMF / PYME).
    """
    template_name = 'moduloETL/carga_datos.html'

    def get_context_data(self, **kwargs):
        estado = EstadoCarga.actual()
        archivo_activo = bool(estado.ruta_csv and os.path.exists(estado.ruta_csv))

        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        cargas_qs = CargaFinanciera.objects.all()
        ratios_qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            cargas_qs = cargas_qs.filter(empresa=empresa_usuario)
            ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
        elif not self.request.user.is_superuser:
            cargas_qs = cargas_qs.none()
            ratios_qs = ratios_qs.none()

        context = {
            'empresa_usuario': empresa_usuario,
            'columnas_plantilla': COLUMNAS_PLANTILLA,
            'archivo_activo': archivo_activo,
            'ruta_archivo_activo': estado.ruta_csv if archivo_activo else None,
            'ultimas_cargas': cargas_qs.select_related('empresa', 'usuario').order_by('-fecha_carga')[:5],
            'total_cargas_historicas': cargas_qs.count(),
            'total_ratios_calculados': ratios_qs.count(),
            'etl_resultado': None,
            'error_mensaje': None,
        }
        context.update(kwargs)
        return context

    def get(self, request: HttpRequest):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest):
        context = self.get_context_data()
        archivo = request.FILES.get('archivo_datos')
        if not archivo:
            context['error_mensaje'] = 'Debe seleccionar un archivo Excel (.xlsx, .xls) o CSV (.csv) para procesar.'
            return render(request, self.template_name, context)

        if archivo.size > 25 * 1024 * 1024:
            context['error_mensaje'] = 'El archivo supera el límite de 25 MB permitido (RNF-10).'
            return render(request, self.template_name, context)

        # Validación obligatoria de aceptación de términos IFRS (Check de certificación)
        terminos_aceptados = request.POST.get('terminos_aceptados')
        if not terminos_aceptados:
            context['error_mensaje'] = 'Debe certificar la exactitud contable del balance y aceptar los Términos de Ingesta, Veracidad y Validación IFRS para procesar el archivo.'
            return render(request, self.template_name, context)

        # Enfoque estricto: El sistema procesa exclusivamente estados financieros horizontales (CMF / IFRS)
        modo_layout = 'horizontal'

        usuario_db = resolver_usuario_bd(request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # 1. Procesamiento desacoplado en memoria con FinancialETLProcessor
        try:
            processor = FinancialETLProcessor(source=archivo, force_layout=modo_layout, auto_process=True)
            features_df = processor.get_features_df()
            audit_report = processor.get_audit_report()

            features_rows = []
            for periodo, row in features_df.iterrows():
                features_rows.append({
                    'periodo': str(periodo),
                    'razon_corriente': float(row['razon_corriente']),
                    'capital_trabajo_sobre_activos': float(row['capital_trabajo_sobre_activos']),
                    'leverage_total': float(row['leverage_total']),
                    'roa_operacional': float(row['roa_operacional']),
                    'margen_operacional': float(row['margen_operacional']),
                    'rotacion_activos': float(row['rotacion_activos']),
                    'volatilidad_flujo_caja': float(row['volatilidad_flujo_caja']),
                })

            cuentas_rows = []
            cuentas_extraidas = audit_report.get('cuentas_extraidas', {})
            for per, ctas in cuentas_extraidas.items():
                item = {'periodo': str(per)}
                item.update(ctas)
                cuentas_rows.append(item)

            json_features = json.dumps(features_df.to_dict(orient='index'))
            json_cuentas = json.dumps(cuentas_extraidas)
            csv_features = json.dumps(features_df.to_csv(index=True))
            nombre_archivo_subido = getattr(archivo, 'name', 'balance_financiero.xlsx')

            etl_resultado = {
                'metadatos': audit_report.get('metadatos', {}) or audit_report.get('metadata', {}),
                'layout': audit_report.get('layout_detectado', 'horizontal'),
                'advertencias': audit_report.get('advertencias', []) or audit_report.get('alertas', []),
                'features_rows': features_rows,
                'cuentas_rows': cuentas_rows,
                'cuentas_dict': cuentas_extraidas,
                'json_features': json_features,
                'json_cuentas': json_cuentas,
                'archivo_nombre': nombre_archivo_subido,
                'csv_features': csv_features,
            }

            # Si el archivo también es un CSV con las columnas clásicas de plantilla, ejecutar persistencia si aplica
            tipo_documento = request.POST.get('tipo_documento', 'Balance General')
            try:
                archivo.seek(0)
                exito, errores, resumen = procesar_e_ingestar_balance(
                    archivo=archivo,
                    tipo_documento=tipo_documento,
                    usuario_db=usuario_db,
                    empresa_default=empresa_usuario
                )
                if exito:
                    cargas_qs = CargaFinanciera.objects.all()
                    ratios_qs = RatioFinanciero.objects.all()
                    if empresa_usuario:
                        cargas_qs = cargas_qs.filter(empresa=empresa_usuario)
                        ratios_qs = ratios_qs.filter(empresa=empresa_usuario)
                    context['ultimas_cargas'] = cargas_qs.select_related('empresa', 'usuario').order_by('-fecha_carga')[:5]
                    context['total_cargas_historicas'] = cargas_qs.count()
                    context['total_ratios_calculados'] = ratios_qs.count()
            except Exception:
                pass

            # Guardar el CSV generado en el EstadoCarga
            try:
                ruta_csv_generada = os.path.join('data', f"etl_features_{usuario_db.id if usuario_db else 'anon'}.csv")
                os.makedirs('data', exist_ok=True)
                features_df.to_csv(ruta_csv_generada)
                estado = EstadoCarga.actual()
                estado.ruta_csv = ruta_csv_generada
                estado.save()
                context['archivo_activo'] = True
                context['ruta_archivo_activo'] = ruta_csv_generada
            except Exception as e:
                logger.warning(f"No se pudo actualizar EstadoCarga: {e}")

            context['etl_resultado'] = etl_resultado
            request.session['etl_resultado'] = etl_resultado
            messages.success(
                request,
                f"¡Archivo «{archivo.name}» procesado exitosamente! Se extrajeron {len(features_rows)} período(s) "
                f"con las 7 razones financieras para Machine Learning."
            )
            return render(request, self.template_name, context)

        except ETLError as exc:
            context['error_mensaje'] = str(exc)
            return render(request, self.template_name, context)
        except Exception as exc:
            logger.exception("Error no controlado en CargaArchivoView")
            context['error_mensaje'] = f"Ocurrió un error inesperado al procesar el archivo: {exc}"
            return render(request, self.template_name, context)


class RatiosFinancierosListView(RolRequeridoMixin, ListView):
    """
    Vista de visualización y auditoría de Ratios Financieros calculados.
    Aislada para mostrar únicamente los ratios pertenecientes a la empresa del usuario.
    """
    model = RatioFinanciero
    template_name = 'moduloETL/ratios_financieros.html'
    context_object_name = 'ratios'
    paginate_by = 20

    def get_queryset(self):
        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        qs = RatioFinanciero.objects.all()
        if empresa_usuario:
            qs = qs.filter(empresa=empresa_usuario)
        elif not self.request.user.is_superuser:
            qs = qs.none()

        periodo = (self.request.GET.get('periodo') or self.request.GET.get('q') or '').strip()
        if periodo:
            qs = qs.filter(
                Q(periodo__icontains=periodo) |
                Q(carga__archivo_origen__icontains=periodo)
            )

        # Ordenamiento por fecha de cálculo (descendente por defecto)
        orden = (self.request.GET.get('orden') or 'desc').strip().lower()
        if orden == 'asc':
            qs = qs.order_by('fecha_calculo', 'id')
        else:
            qs = qs.order_by('-fecha_calculo', '-id')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ratios_qs = self.get_queryset()

        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # Paginador: aprovechamos el conteo que Django ya realizó para no duplicar consultas
        paginator = context.get('paginator')
        total = paginator.count if paginator else ratios_qs.count()

        avg_liquidez = None
        avg_leverage = None
        avg_altman = None

        if total > 0:
            # Agregación SQL directa en base de datos: sin cargar objetos a memoria ni bucles Python
            aggs = ratios_qs.aggregate(
                avg_v1=Avg('v1_razon_corriente'),
                avg_v3=Avg('v3_leverage_total'),
                avg_alt=Avg('ref_z_altman')
            )
            avg_liquidez = round(float(aggs['avg_v1']), 2) if aggs['avg_v1'] is not None else None
            avg_leverage = round(float(aggs['avg_v3']), 2) if aggs['avg_v3'] is not None else None
            avg_altman = round(float(aggs['avg_alt']), 2) if aggs['avg_alt'] is not None else None

        # Detección de outliers para el último ratio (RF-10) optimizada
        page_obj = context.get('page_obj')
        orden = (self.request.GET.get('orden') or 'desc').strip().lower()

        # Si estamos en la página 1 con orden descendente, el último ratio ya fue descargado en el bloque visible
        if page_obj and page_obj.number == 1 and orden != 'asc' and page_obj.object_list:
            ultimo_ratio = page_obj.object_list[0]
        else:
            ultimo_ratio = ratios_qs.order_by('-fecha_calculo', '-id').first()

        anomalias = detectar_anomalias_financieras(ultimo_ratio) if ultimo_ratio else []

        periodo = (self.request.GET.get('periodo') or self.request.GET.get('q') or '').strip()
        orden = (self.request.GET.get('orden') or 'desc').strip().lower()

        context.update({
            'empresa_usuario': empresa_usuario,
            'periodo_busqueda': periodo,
            'q': periodo,
            'orden': orden,
            'total_registros': total,
            'avg_liquidez': avg_liquidez,
            'avg_leverage': avg_leverage,
            'avg_altman': avg_altman,
            'ultimo_ratio': ultimo_ratio,
            'anomalias_detectadas': anomalias,
            'tiene_anomalias': bool(anomalias),
            'total_anomalias': len(anomalias),
        })
        return context


class EjecutarAnalisisView(RolRequeridoMixin, View):
    """
    [RF-11] Permite al Contador / Analista Financiero iniciar manualmente
    la ejecución del modelo predictivo de Random Forest una vez que los datos han sido validados.
    Soporta ejecución individual o en lote (período por período) a partir de los datos
    del ETL en memoria o de registros existentes de RatioFinanciero.
    Redirige automáticamente al Dashboard con las predicciones actualizadas.
    """

    def post(self, request: HttpRequest):
        usuario_db = resolver_usuario_bd(request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # 1. Comprobar si se enviaron características ETL (in-memory) con períodos seleccionados
        features_json_raw = request.POST.get('features_json')
        if not features_json_raw and 'etl_resultado' in request.session:
            session_etl = request.session.get('etl_resultado')
            if isinstance(session_etl, dict) and 'json_features' in session_etl:
                if request.POST.getlist('periodos'):
                    features_json_raw = session_etl['json_features']

        cuentas_json_raw = request.POST.get('cuentas_json')
        if not cuentas_json_raw and 'etl_resultado' in request.session:
            session_etl = request.session.get('etl_resultado')
            if isinstance(session_etl, dict):
                cuentas_json_raw = session_etl.get('json_cuentas')

        cuentas_dict = {}
        if cuentas_json_raw:
            try:
                cuentas_dict = json.loads(cuentas_json_raw) if isinstance(cuentas_json_raw, str) else cuentas_json_raw
            except Exception:
                cuentas_dict = {}

        archivo_nombre = request.POST.get('archivo_nombre')
        if not archivo_nombre and 'etl_resultado' in request.session:
            session_etl = request.session.get('etl_resultado')
            if isinstance(session_etl, dict):
                archivo_nombre = session_etl.get('archivo_nombre')
        if not archivo_nombre:
            archivo_nombre = 'balance_financiero.xlsx'

        periodos_seleccionados = request.POST.getlist('periodos')

        if features_json_raw:
            try:
                if isinstance(features_json_raw, str):
                    features_dict = json.loads(features_json_raw)
                else:
                    features_dict = features_json_raw

                # Si no se especificaron períodos o viene vacío, usar todos los períodos disponibles
                if not periodos_seleccionados:
                    periodos_seleccionados = list(features_dict.keys())

                periodos_a_procesar = [p for p in periodos_seleccionados if p in features_dict]
                if not periodos_a_procesar and features_dict:
                    periodos_a_procesar = list(features_dict.keys())

                if not periodos_a_procesar:
                    messages.warning(request, "No se seleccionó ningún período válido para ejecutar la predicción.")
                    return redirect('moduloETL:carga_datos')

                if not empresa_usuario and usuario_db and usuario_db.empresa:
                    empresa_usuario = usuario_db.empresa
                if not empresa_usuario and hasattr(request.user, 'empresa'):
                    empresa_usuario = request.user.empresa
                if not empresa_usuario:
                    empresa_usuario = Empresa.objects.first()

                predicciones_exitosas = []
                hora_base = timezone.now()

                # Procesar cada período de forma estrictamente individual e independiente
                for i, per in enumerate(periodos_a_procesar):
                    ratios_data = features_dict[per]
                    fecha_periodo = hora_base + timedelta(milliseconds=i * 50)
                    cta = cuentas_dict.get(per, {}) or cuentas_dict.get(str(per), {})

                    # Registrar la información contable en el Historial de Ingesta y Cargas Contables
                    act_circ = Decimal(str(round(float(cta['Activo_Circulante']), 2))) if ('Activo_Circulante' in cta and cta['Activo_Circulante'] is not None) else None
                    pas_circ = Decimal(str(round(float(cta['Pasivo_Circulante']), 2))) if ('Pasivo_Circulante' in cta and cta['Pasivo_Circulante'] is not None) else None
                    act_tot = Decimal(str(round(float(cta['Activo_Total']), 2))) if ('Activo_Total' in cta and cta['Activo_Total'] is not None) else None
                    pas_tot = Decimal(str(round(float(cta['Pasivo_Total']), 2))) if ('Pasivo_Total' in cta and cta['Pasivo_Total'] is not None) else None
                    patrim = Decimal(str(round(float(cta['Patrimonio_Neto']), 2))) if ('Patrimonio_Neto' in cta and cta['Patrimonio_Neto'] is not None) else None
                    ing_net = Decimal(str(round(float(cta['Ingresos_Netos']), 2))) if ('Ingresos_Netos' in cta and cta['Ingresos_Netos'] is not None) else None
                    ebit_val = Decimal(str(round(float(cta['EBIT']), 2))) if ('EBIT' in cta and cta['EBIT'] is not None) else None

                    carga_obj, _ = CargaFinanciera.objects.update_or_create(
                        empresa=empresa_usuario,
                        periodo=str(per),
                        defaults={
                            'fecha_carga': fecha_periodo,
                            'archivo_origen': archivo_nombre,
                            'tipo_carga': 'Balance General',
                            'activo_corriente': act_circ,
                            'pasivo_corriente': pas_circ,
                            'activo_total': act_tot,
                            'pasivo_total': pas_tot,
                            'patrimonio': patrim,
                            'ingresos_netos': ing_net,
                            'ebit': ebit_val,
                            'estado': 'PROCESADO',
                            'usuario': usuario_db,
                        }
                    )

                    ratio_obj, _ = RatioFinanciero.objects.update_or_create(
                        empresa=empresa_usuario,
                        periodo=str(per),
                        defaults={
                            'carga': carga_obj,
                            'fecha_calculo': fecha_periodo,
                            'v1_razon_corriente': Decimal(str(round(float(ratios_data.get('razon_corriente', 1.0)), 4))),
                            'v2_capital_trabajo_activos': Decimal(str(round(float(ratios_data.get('capital_trabajo_sobre_activos', 0.0)), 4))),
                            'v3_leverage_total': Decimal(str(round(float(ratios_data.get('leverage_total', 1.0)), 4))),
                            'v4_roa_operacional': Decimal(str(round(float(ratios_data.get('roa_operacional', 0.0)), 4))),
                            'v5_margen_operacional': Decimal(str(round(float(ratios_data.get('margen_operacional', 0.0)), 4))),
                            'v6_rotacion_activos': Decimal(str(round(float(ratios_data.get('rotacion_activos', 1.0)), 4))),
                            'v7_volatilidad_flujo': Decimal(str(round(float(ratios_data.get('volatilidad_flujo_caja', 0.0)), 4))),
                            'validado': True,
                            'validado_por_usuario': usuario_db,
                            'fecha_validacion': fecha_periodo,
                        }
                    )

                    prediccion, resultado = ejecutar_y_persistir_prediccion(
                        ratio_obj_o_id=ratio_obj,
                        usuario=usuario_db,
                        empresa=empresa_usuario
                    )
                    predicciones_exitosas.append((per, resultado))

                # Al completar la predicción, limpiar el balance cargado en sesión activa
                limpiar_archivos_y_estado()
                request.session.pop('etl_resultado', None)
                request.session.pop('ultimo_resultado', None)

                if len(predicciones_exitosas) == 1:
                    per_nom, res = predicciones_exitosas[0]
                    msg_exito = (
                        f"¡Predicción completada exitosamente para el período '{per_nom}'! "
                        f"Score de Riesgo: {res['score']}% - Nivel: {res['nivel']}."
                    )
                else:
                    nombres = ", ".join([str(p[0]) for p in predicciones_exitosas])
                    msg_exito = (
                        f"¡Se ejecutaron exitosamente {len(predicciones_exitosas)} predicciones independientes "
                        f"para los períodos: {nombres}! Cada período cuenta con su evaluación predictiva en el Dashboard."
                    )

                messages.success(request, msg_exito)
                return redirect('dashboard:dashboard')

            except Exception as exc:
                logger.exception("Error al ejecutar predicciones de períodos ETL: %s", exc)
                messages.error(
                    request,
                    f"No fue posible completar la predicción para los períodos seleccionados: {exc}"
                )
                return redirect('moduloETL:carga_datos')

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
                return redirect('moduloETL:ratios_financieros')
        else:
            ratio_a_ejecutar = ratios_qs.order_by('-fecha_calculo', '-id').first()

        if not ratio_a_ejecutar:
            messages.warning(
                request,
                "No se encontraron ratios financieros cargados para esta empresa. Cargue un balance primero."
            )
            return redirect('moduloETL:carga_datos')

        # Detección de valores anómalos (outliers) previa a la ejecución (RF-10)
        anomalias = detectar_anomalias_financieras(ratio_a_ejecutar)
        forzar_ejecucion = request.POST.get('forzar_ejecucion') in ('1', 'true', 'True')

        if anomalias and not forzar_ejecucion:
            messages.warning(
                request,
                f"Advertencia [RF-10]: Se detectaron {len(anomalias)} valores anómalos o fuera de rango (outliers). "
                "Para proteger la calidad predictiva, confirme la advertencia en el modal antes de ejecutar o corrija los datos."
            )
            return redirect('moduloETL:ratios_financieros')

        try:
            prediccion, resultado = ejecutar_y_persistir_prediccion(
                ratio_obj_o_id=ratio_a_ejecutar,
                usuario=usuario_db,
                empresa=empresa_usuario
            )
            periodo_txt = f" para el período '{ratio_a_ejecutar.periodo}'" if ratio_a_ejecutar.periodo else ""
            msg_exito = (
                f"¡Ejecución de Análisis completada exitosamente{periodo_txt}! "
                f"Score de Riesgo: {resultado['score']}% - Nivel: {resultado['nivel']}."
            )
            if anomalias and forzar_ejecucion:
                msg_exito += f" (Se forzó la ejecución aceptando {len(anomalias)} valor(es) anómalo(s) / outlier(s) detectados)."
            messages.success(request, msg_exito)

            # Al completar la predicción, limpiar el balance cargado en sesión activa
            limpiar_archivos_y_estado()
            request.session.pop('etl_resultado', None)
            request.session.pop('ultimo_resultado', None)
        except Exception as exc:
            logger.exception("Error al ejecutar análisis predictivo desde el módulo ETL: %s", exc)
            messages.error(
                request,
                "No fue posible completar la evaluación del modelo analítico en este momento por una interrupción del servicio. "
                "Por favor, reintente la operación en unos instantes."
            )
            return redirect('moduloETL:ratios_financieros')

        return redirect('dashboard:dashboard')


class HistorialCargasListView(RolRequeridoMixin, ListView):
    """
    Vista de bitácora y trazabilidad de las cargas de balance realizadas
    por o para la empresa del usuario en sesión.
    Soporta búsqueda por texto y ordenamiento por fecha de carga.
    """
    model = CargaFinanciera
    template_name = 'moduloETL/historial_cargas.html'
    context_object_name = 'cargas'
    paginate_by = 25

    def get_queryset(self):
        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # Se enlaza únicamente con 'usuario' que es el dato renderizado en la grilla
        qs = CargaFinanciera.objects.select_related('usuario')
        if empresa_usuario:
            qs = qs.filter(empresa=empresa_usuario)
        elif not self.request.user.is_superuser:
            qs = qs.none()

        # Búsqueda por texto (período, archivo origen, estado, tipo o usuario)
        q = (self.request.GET.get('q') or '').strip()
        if q:
            qs = qs.filter(
                Q(periodo__icontains=q) |
                Q(archivo_origen__icontains=q) |
                Q(estado__icontains=q) |
                Q(tipo_carga__icontains=q) |
                Q(usuario__username__icontains=q)
            )

        # Ordenamiento por fecha de carga (descendente por defecto)
        orden = (self.request.GET.get('orden') or 'desc').strip().lower()
        if orden == 'asc':
            qs = qs.order_by('fecha_carga', 'id')
        else:
            qs = qs.order_by('-fecha_carga', '-id')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_db = resolver_usuario_bd(self.request.user)
        context['empresa_usuario'] = usuario_db.empresa if usuario_db else None
        context['q'] = (self.request.GET.get('q') or '').strip()
        context['orden'] = (self.request.GET.get('orden') or 'desc').strip().lower()
        return context


class LimpiarDatosView(RolRequeridoMixin, View):
    """
    Elimina los archivos de carga temporal y reinicia el EstadoCarga.
    """
    def post(self, request: HttpRequest):
        exito = limpiar_archivos_y_estado()
        request.session.pop('ultimo_resultado', None)
        request.session.pop('etl_resultado', None)
        if exito:
            messages.success(request, "Los datos de la carga activa han sido limpiados correctamente.")
        else:
            messages.warning(request, "No se encontró ningún archivo de carga activo para limpiar.")
        return redirect('moduloETL:carga_datos')


class DescargarPlantillaView(RolRequeridoMixin, View):
    """
    Descarga directamente el archivo Excel estático PlantillaIFRS.xlsx
    almacenado en static/plantillas/.
    """
    def get(self, request: HttpRequest):
        from django.conf import settings
        ruta_archivo = os.path.join(settings.BASE_DIR, 'static', 'plantillas', 'PlantillaIFRS.xlsx')
        if not os.path.exists(ruta_archivo):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_archivo = os.path.join(base_dir, 'plantillas', 'PlantillaIFRS.xlsx')

        with open(ruta_archivo, 'rb') as f:
            contenido = f.read()

        response = HttpResponse(
            contenido,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="PlantillaIFRS.xlsx"'
        return response

