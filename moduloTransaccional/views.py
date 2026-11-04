from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView

from .models import Venta, MetodoPago, RetiroCajaChica, CierreCaja, DetalleCierrePorMetodo
from .forms import VentaForm, CierreCajaForm
from usuarios.models import Usuario


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
    Mixin RBAC reutilizable para vistas basadas en clases.
    Valida si el usuario en sesión tiene alguno de los roles autorizados.
    """
    roles_permitidos = []
    login_url = 'login'

    def get_user_role(self):
        user = self.request.user
        if not user.is_authenticated:
            return None
        # 1. Verifica relación OneToOne PerfilUsuario (AppWeb)
        if hasattr(user, 'perfil') and user.perfil and hasattr(user.perfil, 'rol'):
            return user.perfil.rol
        # 2. Verifica modelo custom Usuario (usuarios.models)
        if hasattr(user, 'rol') and user.rol:
            return user.rol.nombre if hasattr(user.rol, 'nombre') else str(user.rol)
        usuario_db = resolver_usuario_bd(user)
        if usuario_db and usuario_db.rol:
            return usuario_db.rol.nombre
        return None

    def test_func(self):
        # El superusuario de Django tiene acceso para labores de administración
        if self.request.user.is_superuser:
            return True
        rol = self.get_user_role()
        return rol in self.roles_permitidos

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            f"No tienes los permisos requeridos para ingresar a esta sección. "
            f"Rol necesario: {', '.join(self.roles_permitidos)}."
        )
        return redirect('home')


class VentaCreateView(RolRequeridoMixin, CreateView):
    """
    Vista operativa de registro de ventas diarias.
    Exclusiva para el rol 'Trabajador' (y Administrador).
    Calcula automáticamente los campos financieros protegidos antes del guardado.
    """
    model = Venta
    form_class = VentaForm
    template_name = 'moduloTransaccional/venta_form.html'
    success_url = reverse_lazy('moduloTransaccional:venta_crear')
    roles_permitidos = ['Trabajador', 'Administrador']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hoy = timezone.localdate()
        # Muestra las últimas 10 ventas del día para referencia del operador
        context['ventas_hoy'] = Venta.objects.filter(
            fecha__date=fecha_hoy
        ).select_related('metodo_pago').order_by('-fecha')[:10]
        context['fecha_hoy'] = fecha_hoy
        return context

    def form_valid(self, form):
        venta = form.save(commit=False)
        total_bruto = form.cleaned_data['total_bruto']
        descuento_monto = form.cleaned_data.get('descuento_monto') or Decimal('0.00')
        metodo_pago = form.cleaned_data['metodo_pago']

        # -------------------------------------------------------------
        # Fórmulas de Negocio Protegidas (Lógica de Servidor):
        # 1. Total_Cobrado = total_bruto - descuento_monto
        # 2. Comision = Total_Cobrado * (comision_porcentaje / 100)
        # 3. Ingreso_Real = Total_Cobrado - Comision
        # -------------------------------------------------------------
        total_cobrado = total_bruto - descuento_monto
        comision_pct = metodo_pago.comision_porcentaje or Decimal('0.00')
        comision_aplicada = (total_cobrado * (comision_pct / Decimal('100.00'))).quantize(Decimal('0.01'))
        ingreso_real = (total_cobrado - comision_aplicada).quantize(Decimal('0.01'))

        venta.total_bruto = total_bruto
        venta.descuento_tipo = 'Monto' if descuento_monto > Decimal('0.00') else 'Sin Desc'
        venta.descuento_monto = descuento_monto
        venta.total_cobrado = total_cobrado
        venta.comision_aplicada = comision_aplicada
        venta.ingreso_real = ingreso_real

        # Asignar usuario en sesión y fecha
        venta.usuario = resolver_usuario_bd(self.request.user)
        venta.cierre = None
        if not venta.fecha:
            venta.fecha = timezone.now()

        venta.save()

        messages.success(
            self.request,
            f"Venta #{venta.pk} registrada exitosamente. "
            f"Cobrado: ${total_cobrado:,.0f} | Comisión ({comision_pct}%): ${comision_aplicada:,.0f} | "
            f"Ingreso Real: ${ingreso_real:,.0f}."
        )
        return redirect(self.success_url)


class CierreCajaCreateView(RolRequeridoMixin, CreateView):
    """
    Vista de Cierre y Arqueo Diario de Caja.
    Exclusiva para el rol 'Dueño' (y Administrador).
    Garantiza consistencia ACID y previene el doble cierre en la misma fecha.
    """
    model = CierreCaja
    form_class = CierreCajaForm
    template_name = 'moduloTransaccional/cierre_caja_form.html'
    success_url = reverse_lazy('moduloTransaccional:historial_cierres')
    roles_permitidos = ['Dueño', 'Administrador']

    def dispatch(self, request, *args, **kwargs):
        # Bloqueo de Doble Cierre: Si ya existe un cierre con la fecha de hoy, bloquear
        fecha_hoy = timezone.localdate()
        cierre_existente = CierreCaja.objects.filter(fecha=fecha_hoy).first()
        if cierre_existente:
            messages.error(
                request,
                f"El Cierre de Caja del día de hoy ({fecha_hoy.strftime('%d/%m/%Y')}) ya fue registrado "
                f"(ID #{cierre_existente.pk} - Estado: {cierre_existente.estado}). "
                f"No está permitido realizar múltiples cierres en una misma fecha."
            )
            return redirect('moduloTransaccional:historial_cierres')
        return super().dispatch(request, *args, **kwargs)

    def _obtener_datos_del_dia(self):
        """
        Calcula las ventas e ingresos del día huérfanos (sin cierre asignado).
        """
        fecha_hoy = timezone.localdate()
        ventas_huerfanas = Venta.objects.filter(
            cierre__isnull=True,
            fecha__date=fecha_hoy
        )
        retiros_huerfanos = RetiroCajaChica.objects.filter(
            cierre__isnull=True,
            fecha__date=fecha_hoy
        )

        total_ventas_bruto = ventas_huerfanas.aggregate(tot=Sum('total_bruto'))['tot'] or Decimal('0.00')
        total_ingreso_real = ventas_huerfanas.aggregate(tot=Sum('ingreso_real'))['tot'] or Decimal('0.00')
        total_retiros = retiros_huerfanos.aggregate(tot=Sum('monto'))['tot'] or Decimal('0.00')
        total_sistema = total_ingreso_real - total_retiros

        return {
            'fecha_hoy': fecha_hoy,
            'ventas_huerfanas': ventas_huerfanas,
            'retiros_huerfanos': retiros_huerfanos,
            'total_ventas_bruto': total_ventas_bruto,
            'total_ingreso_real': total_ingreso_real,
            'total_retiros': total_retiros,
            'total_sistema': total_sistema,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        datos = self._obtener_datos_del_dia()
        kwargs['total_sistema'] = datos['total_sistema']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datos = self._obtener_datos_del_dia()
        context.update(datos)

        # Desglose de ventas por método de pago para el resumen del arqueo
        resumen_metodos = []
        for mp in MetodoPago.objects.filter(activo=True):
            ventas_mp = datos['ventas_huerfanas'].filter(metodo_pago=mp)
            tot_mp = ventas_mp.aggregate(tot=Sum('ingreso_real'))['tot'] or Decimal('0.00')
            cant_mp = ventas_mp.count()
            resumen_metodos.append({
                'metodo': mp,
                'cantidad': cant_mp,
                'total_ingreso_real': tot_mp
            })
        context['resumen_metodos'] = resumen_metodos
        return context

    def form_valid(self, form):
        datos = self._obtener_datos_del_dia()
        total_sistema = datos['total_sistema']
        total_retiros = datos['total_retiros']
        fecha_hoy = datos['fecha_hoy']

        total_arqueo = form.cleaned_data['total_arqueo']
        justificacion = form.cleaned_data.get('justificacion', '').strip()
        descuadre = total_arqueo - total_sistema

        try:
            # -------------------------------------------------------------
            # Transaccionalidad ACID con rollback ante cualquier excepción
            # -------------------------------------------------------------
            with transaction.atomic():
                cierre = form.save(commit=False)
                cierre.fecha = fecha_hoy
                cierre.estado = 'Cuadrado' if descuadre == Decimal('0.00') else 'Descuadrado'
                cierre.total_sistema = total_sistema
                cierre.total_retiros = total_retiros
                cierre.total_arqueo = total_arqueo
                cierre.descuadre_total = descuadre
                cierre.cerrado_por_usuario = resolver_usuario_bd(self.request.user)
                cierre.fecha_confirmacion = timezone.now()
                cierre.save()

                # 1. Asociar todas las Ventas huérfanas de hoy al nuevo cierre
                ventas_actualizadas = Venta.objects.filter(
                    cierre__isnull=True,
                    fecha__date=fecha_hoy
                ).update(cierre=cierre)

                # 2. Asociar todos los Retiros huérfanos de hoy al nuevo cierre
                retiros_actualizados = RetiroCajaChica.objects.filter(
                    cierre__isnull=True,
                    fecha__date=fecha_hoy
                ).update(cierre=cierre)

                # 3. Crear detalles por cada método de pago para auditoría
                for mp in MetodoPago.objects.filter(activo=True):
                    ventas_mp = Venta.objects.filter(cierre=cierre, metodo_pago=mp)
                    tot_mp = ventas_mp.aggregate(tot=Sum('ingreso_real'))['tot'] or Decimal('0.00')
                    
                    # Generar detalle si tuvo movimiento o para registrar la cuadratura
                    if tot_mp > Decimal('0.00') or mp.nombre == 'Efectivo':
                        DetalleCierrePorMetodo.objects.create(
                            cierre=cierre,
                            metodo_pago=mp,
                            total_sistema=tot_mp,
                            total_arqueo=total_arqueo if mp.nombre == 'Efectivo' else tot_mp,
                            descuadre=descuadre if mp.nombre == 'Efectivo' else Decimal('0.00'),
                            justificacion=justificacion if (mp.nombre == 'Efectivo' and descuadre != Decimal('0.00')) else None
                        )

            messages.success(
                self.request,
                f"Cierre de caja #{cierre.pk} completado con éxito. "
                f"Ventas consolidadas: {ventas_actualizadas} | Retiros consolidados: {retiros_actualizados} | "
                f"Estado: {cierre.estado} (Descuadre: ${descuadre:,.2f})."
            )
            return redirect(self.success_url)

        except Exception as e:
            messages.error(
                self.request,
                f"Error crítico al registrar el cierre de caja. La transacción fue revertida: {str(e)}"
            )
            return self.form_invalid(form)


class HistorialCierresListView(RolRequeridoMixin, ListView):
    """
    Vista de consulta y auditoría de Cierres de Caja.
    Permitida para los roles 'Dueño' y 'Contador' (y Administrador).
    Lista los registros en orden cronológico descendente.
    """
    model = CierreCaja
    template_name = 'moduloTransaccional/cierrecaja_list.html'
    context_object_name = 'cierres'
    ordering = ['-fecha']
    paginate_by = 15
    roles_permitidos = ['Dueño', 'Contador', 'Administrador']

    def get_queryset(self):
        return CierreCaja.objects.all().select_related(
            'cerrado_por_usuario',
            'revisado_por_usuario'
        ).order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hoy = timezone.localdate()
        context['cierre_hoy_existe'] = CierreCaja.objects.filter(fecha=fecha_hoy).exists()
        context['fecha_hoy'] = fecha_hoy
        return context
