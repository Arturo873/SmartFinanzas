"""
Vistas de la Capa de Presentación Gerencial (Dashboard).
SmartFinanzas - Arquitectura Monolito Modular.

Esta app NO define modelos de base de datos propios. Inyecta dependencias
de lectura de moduloETL, moduloTransaccional y capaAnalitica para renderizar
el panel gerencial interactivo y emitir informes ejecutivos en PDF.
"""

import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

# Dependencias de lectura de las otras aplicaciones del monolito
from usuarios.models import Usuario, Empresa
from AppWeb.models import PerfilUsuario
from moduloETL.models import RatioFinanciero
from moduloTransaccional.models import Venta
from capaAnalitica.models import PrediccionRiesgo
from capaAnalitica.services import MotorRiesgo, ejecutar_y_persistir_prediccion
from .pdf_generator import construir_informe_ejecutivo_pdf


def resolver_usuario_bd(auth_user):
    """
    Obtiene la entidad Usuario de la base de datos a partir del usuario Django en sesión.
    """
    if not auth_user or not auth_user.is_authenticated:
        return None
    if isinstance(auth_user, Usuario):
        return auth_user
    usuario_db = Usuario.objects.filter(username=auth_user.username).first()
    if not usuario_db and hasattr(auth_user, 'email'):
        usuario_db = Usuario.objects.filter(email=auth_user.email).first()
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

        # Última Predicción de Riesgo generada
        ultima_prediccion = predicciones_qs.order_by('-fecha_prediccion', '-id').first()

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

        # 3. Consulta de las últimas 5 a 10 PrediccionRiesgo para la curva de tendencia
        ultimas_predicciones = list(predicciones_qs.order_by('-fecha_prediccion', '-id')[:10])
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

        ultimo_ratio = ratios_qs.order_by('-fecha_calculo', '-id').first()

        # 5. Entrega de datos al contexto (incluyendo JSON serializado seguro para Chart.js y UI)
        context.update({
            'empresa_usuario': empresa_usuario,
            'usuario_rol': self.get_user_role(),
            'ultima_prediccion': ultima_prediccion,
            'score': score,
            'nivel': nivel,
            'fecha_prediccion': fecha_prediccion,
            'top_3_variables': top_3_variables,
            'ingreso_real_hoy': ingreso_real_hoy,
            'total_ventas_hoy': total_ventas_hoy,
            'ultimo_ratio': ultimo_ratio,
            'total_predicciones_historicas': predicciones_qs.count(),
            # JSON seguro para el frontend
            'chart_fechas_json': json.dumps(chart_fechas, ensure_ascii=False),
            'chart_scores_json': json.dumps(chart_scores),
            'chart_niveles_json': json.dumps(chart_niveles),
            'chart_es_actual_json': json.dumps(chart_es_actual),
            'top_3_shap_json': json.dumps(top_3_variables, ensure_ascii=False),
        })

        return context


class GenerarPDFView(DashboardRolMixin, View):
    """
    Controlador para exportar el Informe Ejecutivo en PDF utilizando ReportLab.
    Permite a los directivos descargar el diagnóstico formal de riesgo y explicabilidad.
    """

    def get(self, request: HttpRequest):
        usuario_db = resolver_usuario_bd(request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        predicciones_qs = PrediccionRiesgo.objects.select_related('empresa', 'ratio')
        if empresa_usuario:
            predicciones_qs = predicciones_qs.filter(empresa=empresa_usuario)
        elif not request.user.is_superuser:
            predicciones_qs = predicciones_qs.none()

        ultima_prediccion = predicciones_qs.order_by('-fecha_prediccion', '-id').first()

        top_3_variables = []
        if ultima_prediccion and ultima_prediccion.variables_influyentes:
            try:
                top_3_variables = json.loads(ultima_prediccion.variables_influyentes)
            except Exception:
                top_3_variables = []

        hoy = timezone.localdate()
        ventas_hoy_qs = Venta.objects.filter(fecha__date=hoy)
        if empresa_usuario:
            ventas_hoy_qs = ventas_hoy_qs.filter(empresa=empresa_usuario)
        elif not request.user.is_superuser:
            ventas_hoy_qs = ventas_hoy_qs.none()

        ingreso_real_hoy = ventas_hoy_qs.aggregate(total=Sum('ingreso_real'))['total'] or Decimal('0.00')
        total_ventas_hoy = ventas_hoy_qs.count()

        pdf_buffer = construir_informe_ejecutivo_pdf(
            empresa=empresa_usuario,
            ultima_prediccion=ultima_prediccion,
            top_3_variables=top_3_variables,
            ingreso_real_hoy=ingreso_real_hoy,
            usuario=usuario_db or request.user,
            total_ventas_hoy=total_ventas_hoy,
        )

        nombre_archivo = f"informe_ejecutivo_riesgo_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response


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

        ultimo_ratio = ratios_qs.order_by('-fecha_calculo', '-id').first()

        if not ultimo_ratio:
            messages.warning(
                request,
                "No se encontraron ratios financieros cargados para esta empresa. Cargue un balance en el Módulo ETL primero."
            )
            return redirect('dashboard:dashboard')

        try:
            prediccion, resultado = ejecutar_y_persistir_prediccion(
                ratio_obj_o_id=ultimo_ratio,
                usuario=usuario_db,
                empresa=empresa_usuario
            )
            messages.success(
                request,
                f"¡Nueva predicción ejecutada exitosamente! Score: {resultado['score']}% - Nivel: {resultado['nivel']}."
            )
        except Exception as e:
            messages.error(request, f"Error al ejecutar la predicción con el modelo de Machine Learning: {e}")

        return redirect('dashboard:dashboard')
