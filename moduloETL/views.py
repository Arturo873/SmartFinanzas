"""
Vistas del Módulo ETL (Extract, Transform, Load) de SmartFinanzas.
Implementa aislamiento por empresa (multi-tenant): los usuarios solo pueden ver
y gestionar información financiera perteneciente a su propia empresa.
"""

import os
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, FormView

from .models import CargaFinanciera, RatioFinanciero
from .forms import CargaArchivoForm
from .services import (
    procesar_e_ingestar_balance,
    limpiar_archivos_y_estado,
    generar_plantilla_ejemplo_csv,
    COLUMNAS_PLANTILLA,
)
from usuarios.models import Usuario, Empresa
from AppWeb.models import EstadoCarga


def resolver_usuario_bd(auth_user):
    """
    Obtiene la instancia de 'Usuario' (tabla usuario) correspondiente
    al usuario autenticado en la sesión de Django.
    """
    if not auth_user or not auth_user.is_authenticated:
        return None
    if isinstance(auth_user, Usuario):
        return auth_user
    usuario_db = Usuario.objects.filter(username=auth_user.username).first()
    if not usuario_db and hasattr(auth_user, 'email'):
        usuario_db = Usuario.objects.filter(email=auth_user.email).first()
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


class CargaArchivoView(RolRequeridoMixin, FormView):
    """
    Vista principal de Ingesta y Carga de Archivos Contables.
    Gestiona el formulario de subida, ejecuta el pipeline ETL y asocia los datos
    exclusivamente a la empresa del usuario autenticado.
    """
    template_name = 'moduloETL/carga_datos.html'
    form_class = CargaArchivoForm
    success_url = reverse_lazy('moduloETL:ratios_financieros')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        context.update({
            'empresa_usuario': empresa_usuario,
            'columnas_plantilla': COLUMNAS_PLANTILLA,
            'archivo_activo': archivo_activo,
            'ruta_archivo_activo': estado.ruta_csv if archivo_activo else None,
            'ultimas_cargas': cargas_qs.select_related('empresa', 'usuario').order_by('-fecha_carga')[:5],
            'total_cargas_historicas': cargas_qs.count(),
            'total_ratios_calculados': ratios_qs.count(),
        })
        return context

    def form_valid(self, form):
        archivo = form.cleaned_data['archivo_datos']
        tipo_documento = form.cleaned_data['tipo_documento']

        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # Ejecución del Pipeline ETL vinculado a la empresa del usuario
        exito, errores, resumen = procesar_e_ingestar_balance(
            archivo=archivo,
            tipo_documento=tipo_documento,
            usuario_db=usuario_db,
            empresa_default=empresa_usuario
        )

        if not exito:
            for error in errores:
                messages.error(self.request, error)
            messages.warning(
                self.request,
                "El archivo no fue persistido debido a los errores detectados. Por favor corrija el documento y reintente."
            )
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"¡Archivo «{resumen['nombre_archivo']}» ingestó y procesó exitosamente! "
            f"Se validaron y cargaron {resumen['cargas_creadas']} registro(s) contable(s) "
            f"para {empresa_usuario.razon_social if empresa_usuario else 'tu empresa'} "
            f"y se calcularon automáticamente sus ratios predictivos (V1-V7) y de solvencia."
        )
        return redirect('moduloETL:ratios_financieros')


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

        qs = RatioFinanciero.objects.select_related('carga', 'empresa', 'validado_por_usuario').order_by('-fecha_calculo')
        if empresa_usuario:
            qs = qs.filter(empresa=empresa_usuario)
        elif not self.request.user.is_superuser:
            qs = qs.none()

        periodo = self.request.GET.get('periodo')
        if periodo:
            qs = qs.filter(periodo__icontains=periodo.strip())

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ratios_qs = self.get_queryset()

        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        # KPIs agregados para la empresa del usuario
        total = ratios_qs.count()
        avg_liquidez = None
        avg_leverage = None
        avg_altman = None

        if total > 0:
            import numpy as np
            v1_vals = [float(r.v1_razon_corriente) for r in ratios_qs if r.v1_razon_corriente is not None]
            v3_vals = [float(r.v3_leverage_total) for r in ratios_qs if r.v3_leverage_total is not None]
            alt_vals = [float(r.ref_z_altman) for r in ratios_qs if r.ref_z_altman is not None]

            avg_liquidez = round(float(np.mean(v1_vals)), 2) if v1_vals else None
            avg_leverage = round(float(np.mean(v3_vals)), 2) if v3_vals else None
            avg_altman = round(float(np.mean(alt_vals)), 2) if alt_vals else None

        context.update({
            'empresa_usuario': empresa_usuario,
            'periodo_busqueda': self.request.GET.get('periodo', ''),
            'total_registros': total,
            'avg_liquidez': avg_liquidez,
            'avg_leverage': avg_leverage,
            'avg_altman': avg_altman,
        })
        return context


class HistorialCargasListView(RolRequeridoMixin, ListView):
    """
    Vista de bitácora y trazabilidad de las cargas de balance realizadas
    por o para la empresa del usuario en sesión.
    """
    model = CargaFinanciera
    template_name = 'moduloETL/historial_cargas.html'
    context_object_name = 'cargas'
    paginate_by = 25

    def get_queryset(self):
        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        qs = CargaFinanciera.objects.select_related('empresa', 'usuario').order_by('-fecha_carga')
        if empresa_usuario:
            qs = qs.filter(empresa=empresa_usuario)
        elif not self.request.user.is_superuser:
            qs = qs.none()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_db = resolver_usuario_bd(self.request.user)
        context['empresa_usuario'] = usuario_db.empresa if usuario_db else None
        return context


class LimpiarDatosView(RolRequeridoMixin, View):
    """
    Elimina los archivos de carga temporal y reinicia el EstadoCarga.
    """
    def post(self, request: HttpRequest):
        exito = limpiar_archivos_y_estado()
        request.session.pop('ultimo_resultado', None)
        if exito:
            messages.success(request, "Los datos de la carga activa han sido limpiados correctamente.")
        else:
            messages.warning(request, "No se encontró ningún archivo de carga activo para limpiar.")
        return redirect('moduloETL:carga_datos')


class DescargarPlantillaView(RolRequeridoMixin, View):
    """
    Permite descargar una plantilla oficial en formato CSV con la estructura
    y formato exigido por el pipeline ETL.
    """
    def get(self, request: HttpRequest):
        contenido_csv = generar_plantilla_ejemplo_csv()
        response = HttpResponse(contenido_csv, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="plantilla_estados_financieros_smartfinanzas.csv"'
        return response
