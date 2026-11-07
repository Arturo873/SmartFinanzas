import logging
from decimal import Decimal, InvalidOperation, DivisionByZero, Overflow
from django.db import transaction, DatabaseError, OperationalError
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

logger = logging.getLogger(__name__)


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

    Principios de Programación Defensiva aplicados:
    - Verificación proactiva de condiciones de borde (guard clauses).
    - Prevención de operaciones ilógicas (ventas <= $0, cobros negativos o nulos).
    - Aislamiento en transacciones ACID con manejo de excepciones y rollback automático.
    - Generación de alertas claras y accionables (problema, causa y solución).
    """
    model = Venta
    form_class = VentaForm
    template_name = 'moduloTransaccional/venta_form.html'
    success_url = reverse_lazy('moduloTransaccional:venta_crear')
    roles_permitidos = ['Trabajador', 'Administrador']

    def dispatch(self, request, *args, **kwargs):
        # Verificación defensiva previa: comprobar si la caja de hoy ya fue cerrada
        fecha_hoy = timezone.localdate()
        cierre_hoy = CierreCaja.objects.filter(fecha=fecha_hoy).first()
        if cierre_hoy and request.method == 'POST':
            messages.error(
                request,
                f"Operación bloqueada: La caja del día ({fecha_hoy.strftime('%d/%m/%Y')}) ya fue cerrada "
                f"(ID #{cierre_hoy.pk} - Estado: {cierre_hoy.estado}). "
                f"Motivo: No se pueden añadir ventas a una caja con arqueo cerrado. "
                f"Solución: Para registrar ventas rezagadas o ajustes extraordinarios, contacta al Administrador o Dueño del turno."
            )
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hoy = timezone.localdate()
        try:
            # Consulta segura con límite defensivo y captura de excepciones
            context['ventas_hoy'] = Venta.objects.filter(
                fecha__date=fecha_hoy
            ).select_related('metodo_pago').order_by('-fecha')[:10]
        except Exception as e:
            logger.error(f"Error al consultar historial de ventas del día: {e}", exc_info=True)
            context['ventas_hoy'] = []
            messages.warning(
                self.request,
                "Aviso del sistema: No fue posible cargar el listado de ventas recientes del día. "
                "El registro de nuevas ventas sigue operativo."
            )

        context['fecha_hoy'] = fecha_hoy
        context['cierre_hoy'] = CierreCaja.objects.filter(fecha=fecha_hoy).first()
        return context

    def form_invalid(self, form):
        """
        Manejo defensivo ante fallos de validación en el formulario.
        Genera alertas amigables y detalladas con la causa y la solución para el usuario.
        """
        errores_lista = []
        for campo, errs in form.errors.items():
            nombre_campo = form.fields[campo].label if campo in form.fields and form.fields[campo].label else campo
            for err in errs:
                errores_lista.append(f"{nombre_campo}: {err}")

        resumen_errores = " | ".join(errores_lista) if errores_lista else "Verifique los campos obligatorios."
        messages.error(
            self.request,
            f"No fue posible registrar la venta debido a errores de validación: {resumen_errores}. "
            f"Solución: Corrija los valores señalados en el formulario e intente presionar 'Registrar Venta' nuevamente."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        # -------------------------------------------------------------
        # 1. VALIDACIONES DEFENSIVAS DE NEGOCIO Y SANEAMIENTO DE DATOS
        # -------------------------------------------------------------
        fecha_hoy = timezone.localdate()

        # A. Bloqueo de seguridad: No procesar ventas en turnos cerrados
        cierre_existente = CierreCaja.objects.filter(fecha=fecha_hoy).first()
        if cierre_existente:
            messages.error(
                self.request,
                f"Operación rechazada: La caja del día ({fecha_hoy.strftime('%d/%m/%Y')}) ya se encuentra cerrada "
                f"(Cierre #{cierre_existente.pk} - Estado: {cierre_existente.estado}). "
                f"Motivo: Registrar nuevas transacciones corrompería la auditoría del arqueo de hoy. "
                f"Solución: Si se trata de una venta fuera de horario o turno cerrado, solicite autorización al Administrador."
            )
            return self.form_invalid(form)

        # B. Validación de variables críticas nulas o vacías
        total_bruto = form.cleaned_data.get('total_bruto')
        if total_bruto is None:
            form.add_error('total_bruto', "El total bruto de la venta no puede estar vacío.")
            messages.error(
                self.request,
                "Validación de datos fallida: El campo 'Total Bruto' no contiene ningún valor. "
                "Solución: Ingrese un importe numérico mayor a 0."
            )
            return self.form_invalid(form)

        metodo_pago = form.cleaned_data.get('metodo_pago')
        if not metodo_pago:
            form.add_error('metodo_pago', "Debe seleccionar un método de pago activo.")
            messages.error(
                self.request,
                "Validación de datos fallida: No se seleccionó un medio de pago para la transacción. "
                "Solución: Seleccione una opción válida de la lista desplegable (Efectivo, Débito, Transferencia, etc.)."
            )
            return self.form_invalid(form)

        if not metodo_pago.activo:
            form.add_error('metodo_pago', f"El método de pago '{metodo_pago.nombre}' no se encuentra habilitado.")
            messages.error(
                self.request,
                f"Operación rechazada: El método '{metodo_pago.nombre}' fue deshabilitado en el sistema. "
                f"Solución: Seleccione un método de pago activo o solicite su activación al Administrador."
            )
            return self.form_invalid(form)

        # C. Validación de negocio: No procesar ventas con valor 0 o negativo
        if total_bruto <= Decimal('0.00'):
            form.add_error('total_bruto', "El total bruto de la venta debe ser estrictamente mayor a 0.")
            messages.error(
                self.request,
                f"Operación ilógica rechazada: No se pueden registrar ventas por un valor de ${total_bruto:,.2f}. "
                f"Motivo: Toda venta debe representar un flujo de ingreso comercial positivo mayor a $0. "
                f"Solución: Ingrese el monto real y positivo de los productos o servicios comercializados."
            )
            return self.form_invalid(form)

        # Límite superior razonable para evitar desbordamiento numérico o digitación accidental
        max_venta_permitida = Decimal('99999999.99')
        if total_bruto > max_venta_permitida:
            form.add_error('total_bruto', f"El importe excede el límite máximo por transacción (${max_venta_permitida:,.0f}).")
            messages.error(
                self.request,
                f"Alerta de seguridad: El total bruto (${total_bruto:,.2f}) supera el tope por transacción del sistema. "
                f"Solución: Verifique que no haya ingresado ceros adicionales accidentalmente."
            )
            return self.form_invalid(form)

        # D. Validación defensiva de descuentos
        descuento_monto = form.cleaned_data.get('descuento_monto')
        if descuento_monto is None:
            descuento_monto = Decimal('0.00')

        if descuento_monto < Decimal('0.00'):
            form.add_error('descuento_monto', "El descuento no puede ser un valor negativo.")
            messages.error(
                self.request,
                "Operación ilógica rechazada: El descuento ingresado es negativo. "
                "Solución: Ingrese un valor mayor o igual a $0 o déjelo en blanco si no aplica descuento."
            )
            return self.form_invalid(form)

        # E. Validación de coherencia comercial: el valor a cobrar debe ser positivo
        total_cobrado = total_bruto - descuento_monto
        if total_cobrado <= Decimal('0.00'):
            form.add_error('descuento_monto', "El descuento no puede igualar o exceder el total bruto.")
            messages.error(
                self.request,
                f"Operación ilógica rechazada: El descuento (${descuento_monto:,.2f}) cubre o supera el 100% de la venta (${total_bruto:,.2f}), "
                f"resultando en un valor a cobrar de ${total_cobrado:,.2f}. "
                f"Motivo: El total cobrado al cliente debe ser estrictamente mayor a $0. "
                f"Solución: Ajuste el descuento para que sea menor al total bruto."
            )
            return self.form_invalid(form)

        # F. Validación de Usuario y Organización (Multi-tenancy)
        usuario_db = resolver_usuario_bd(self.request.user)
        if not usuario_db:
            messages.error(
                self.request,
                "Error de sesión de usuario: No fue posible validar la cuenta activa del operador en el sistema. "
                "Solución: Cierre sesión, vuelva a iniciar sesión e intente nuevamente."
            )
            return self.form_invalid(form)

        if not usuario_db.empresa and not self.request.user.is_superuser:
            messages.error(
                self.request,
                "Error de configuración empresarial: Tu perfil de usuario no está vinculado a ninguna empresa activa. "
                "Motivo: Toda operación transaccional debe imputarse a una empresa para mantener la integridad contable. "
                "Solución: Solicita al Administrador del sistema asignar tu usuario a una Empresa."
            )
            return self.form_invalid(form)

        # -------------------------------------------------------------
        # 2. MANEJO DE EXCEPCIONES EN OPERACIONES CRÍTICAS (CÁLCULOS Y DIVISIÓN)
        # -------------------------------------------------------------
        try:
            # Control defensivo de comisión: rango 0% a 100%
            comision_pct = metodo_pago.comision_porcentaje or Decimal('0.00')
            if comision_pct < Decimal('0.00') or comision_pct > Decimal('100.00'):
                raise ValueError(
                    f"El porcentaje de comisión configurado ({comision_pct}%) está fuera del rango admitido (0% a 100%)."
                )

            divisor_cien = Decimal('100.00')
            if divisor_cien <= Decimal('0.00'):
                raise ZeroDivisionError("División por cero en el cálculo porcentual de comisión.")

            comision_factor = comision_pct / divisor_cien
            comision_aplicada = (total_cobrado * comision_factor).quantize(Decimal('0.01'))
            ingreso_real = (total_cobrado - comision_aplicada).quantize(Decimal('0.01'))

            if ingreso_real < Decimal('0.00'):
                raise ValueError("El ingreso real calculado resulta en un valor negativo.")

        except (InvalidOperation, DivisionByZero, Overflow, OverflowError, ValueError, TypeError) as calc_err:
            logger.error(f"Falla aritmética defensiva en VentaCreateView: {calc_err}", exc_info=True)
            messages.error(
                self.request,
                f"Error en el cálculo financiero: {calc_err}. "
                f"Motivo: Falló la fórmula de deducción de comisiones para '{metodo_pago.nombre}'. "
                f"Solución: Verifique los valores ingresados y confirme con administración la comisión del método de pago."
            )
            return self.form_invalid(form)

        # -------------------------------------------------------------
        # 3. TRANSACCIONALIDAD ACID Y MANEJO DE EXCEPCIONES DE PERSISTENCIA
        # -------------------------------------------------------------
        try:
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.total_bruto = total_bruto
                venta.descuento_tipo = 'Monto' if descuento_monto > Decimal('0.00') else 'Sin Desc'
                venta.descuento_monto = descuento_monto
                venta.total_cobrado = total_cobrado
                venta.comision_aplicada = comision_aplicada
                venta.ingreso_real = ingreso_real
                venta.usuario = usuario_db
                if usuario_db and usuario_db.empresa:
                    venta.empresa = usuario_db.empresa
                venta.cierre = None
                if not venta.fecha:
                    venta.fecha = timezone.now()

                venta.save()

            messages.success(
                self.request,
                f"✓ Venta #{venta.pk} registrada exitosamente. "
                f"Total Cobrado: ${total_cobrado:,.0f} | Comisión ({comision_pct}%): ${comision_aplicada:,.0f} | "
                f"Ingreso Real para Caja: ${ingreso_real:,.0f}."
            )
            return redirect(self.success_url)

        except (OperationalError, DatabaseError) as db_err:
            logger.error(f"Error de persistencia en VentaCreateView: {db_err}", exc_info=True)
            messages.error(
                self.request,
                "No fue posible completar el registro de la venta debido a una interrupción temporal del servicio. "
                "Tus datos siguen cargados en el formulario. Por favor, reintenta presionar 'Registrar Venta' en unos momentos o contacta a soporte si la situación persiste."
            )
            return self.form_invalid(form)

        except Exception as exc:
            logger.exception(f"Excepción inesperada en VentaCreateView: {exc}")
            messages.error(
                self.request,
                "No fue posible procesar la solicitud en este momento por una inconsistencia imprevista. "
                "Tus datos se conservan en pantalla. Por favor, reintenta la operación o contacta al equipo de soporte."
            )
            return self.form_invalid(form)


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

    def form_invalid(self, form):
        """
        Manejo defensivo ante fallos de validación en el cierre de caja.
        Genera alertas con descripción clara del problema y los pasos de solución.
        """
        errores_lista = []
        for campo, errs in form.errors.items():
            nombre_campo = form.fields[campo].label if campo in form.fields and form.fields[campo].label else campo
            for err in errs:
                errores_lista.append(f"{nombre_campo}: {err}")

        resumen_errores = " | ".join(errores_lista) if errores_lista else "Verifique los montos del arqueo."
        messages.error(
            self.request,
            f"No se pudo completar el cierre de caja: {resumen_errores}. "
            f"Solución: Verifique los valores contados e ingrese la justificación requerida si existe descuadre."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        # 1. Validación defensiva de datos y estado del día
        try:
            datos = self._obtener_datos_del_dia()
        except Exception as e:
            logger.error(f"Error al obtener datos del día para cierre: {e}", exc_info=True)
            messages.error(
                self.request,
                "Error al consolidar la información del turno para el arqueo. "
                "Motivo: No se pudieron calcular las ventas o retiros del día. "
                "Solución: Verifique la conectividad del sistema e intente recargar la página."
            )
            return self.form_invalid(form)

        total_sistema = datos['total_sistema']
        total_retiros = datos['total_retiros']
        fecha_hoy = datos['fecha_hoy']

        total_arqueo = form.cleaned_data.get('total_arqueo')
        if total_arqueo is None:
            form.add_error('total_arqueo', "El total de arqueo físico es obligatorio.")
            messages.error(
                self.request,
                "Validación de datos fallida: No se ingresó el monto de arqueo físico. "
                "Solución: Realice el recuento de efectivo en caja e ingrese el total."
            )
            return self.form_invalid(form)

        if total_arqueo < Decimal('0.00'):
            form.add_error('total_arqueo', "El arqueo físico no puede ser negativo.")
            messages.error(
                self.request,
                "Operación ilógica rechazada: El arqueo físico no puede ser un monto negativo. "
                "Solución: Ingrese un valor mayor o igual a $0."
            )
            return self.form_invalid(form)

        justificacion = (form.cleaned_data.get('justificacion') or '').strip()
        descuadre = total_arqueo - total_sistema

        if descuadre != Decimal('0.00') and not justificacion:
            signo = "+" if descuadre > Decimal('0.00') else "-"
            form.add_error('justificacion', "Debe justificar obligatoriamente el descuadre detectado.")
            messages.error(
                self.request,
                f"Validación de auditoría requerida: Se detectó un descuadre de {signo}${abs(descuadre):,.2f}. "
                f"Motivo: La normativa interna exige un registro explicativo de cualquier diferencia con el sistema. "
                f"Solución: Complete el campo 'Justificación de Descuadre' indicando el motivo de la discrepancia."
            )
            return self.form_invalid(form)

        # 2. Transaccionalidad ACID y manejo robusto de excepciones
        try:
            with transaction.atomic():
                cierre = form.save(commit=False)
                cierre.fecha = fecha_hoy
                cierre.estado = 'Cuadrado' if descuadre == Decimal('0.00') else 'Descuadrado'
                cierre.total_sistema = total_sistema
                cierre.total_retiros = total_retiros
                cierre.total_arqueo = total_arqueo
                cierre.descuadre_total = descuadre
                usuario_db = resolver_usuario_bd(self.request.user)
                cierre.cerrado_por_usuario = usuario_db
                if usuario_db and usuario_db.empresa:
                    cierre.empresa = usuario_db.empresa
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
                f"✓ Cierre de caja #{cierre.pk} completado con éxito. "
                f"Ventas consolidadas: {ventas_actualizadas} | Retiros consolidados: {retiros_actualizados} | "
                f"Estado: {cierre.estado} (Descuadre: ${descuadre:,.2f})."
            )
            return redirect(self.success_url)

        except (OperationalError, DatabaseError) as db_err:
            logger.error(f"Error de persistencia en CierreCajaCreateView: {db_err}", exc_info=True)
            messages.error(
                self.request,
                "No fue posible completar el cierre de caja debido a una interrupción temporal del servicio. "
                "La operación fue cancelada de forma segura para proteger los registros de las ventas. "
                "Solución: Por favor, reintenta presionar 'Confirmar Cierre' en unos momentos."
            )
            return self.form_invalid(form)

        except Exception as e:
            logger.exception(f"Error crítico en CierreCajaCreateView: {e}")
            messages.error(
                self.request,
                "Ocurrió un problema imprevisto al procesar el cierre de caja. "
                "La operación fue cancelada de forma segura para proteger la integridad contable. "
                "Solución: Revise los montos e intente nuevamente; si la situación persiste, informe al equipo de soporte."
            )
            return self.form_invalid(form)


class HistorialCierresListView(RolRequeridoMixin, ListView):
    """
    Vista de consulta y auditoría de Cierres de Caja.
    Permitida para los roles 'Dueño' y 'Contador' (y Administrador).
    Permite búsqueda automática por texto o selección por calendario (día),
    además de ordenamiento ascendente/descendente por fecha.
    """
    model = CierreCaja
    template_name = 'moduloTransaccional/cierrecaja_list.html'
    context_object_name = 'cierres'
    paginate_by = 15
    roles_permitidos = ['Dueño', 'Contador', 'Administrador']

    def get_queryset(self):
        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        qs = CierreCaja.objects.all().select_related(
            'cerrado_por_usuario',
            'revisado_por_usuario',
            'empresa'
        )
        if empresa_usuario:
            qs = qs.filter(empresa=empresa_usuario)
        elif not self.request.user.is_superuser:
            qs = qs.none()

        # Filtro de búsqueda por fecha seleccionada en calendario (formato YYYY-MM-DD)
        fecha_filtro = (self.request.GET.get('fecha') or '').strip()
        if fecha_filtro:
            try:
                from datetime import datetime
                fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                qs = qs.filter(fecha=fecha_obj)
            except (ValueError, TypeError):
                pass

        # Búsqueda automática por texto libre (estado, usuario, o fecha escrita)
        q = (self.request.GET.get('q') or '').strip()
        if q:
            filtro_q = (
                Q(estado__icontains=q) |
                Q(cerrado_por_usuario__username__icontains=q) |
                Q(cerrado_por_usuario__email__icontains=q)
            )
            try:
                from datetime import datetime
                if '/' in q:
                    fecha_p = datetime.strptime(q, '%d/%m/%Y').date()
                    filtro_q |= Q(fecha=fecha_p)
                elif '-' in q and len(q.split('-')[0]) == 4:
                    fecha_p = datetime.strptime(q, '%Y-%m-%d').date()
                    filtro_q |= Q(fecha=fecha_p)
            except Exception:
                pass
            qs = qs.filter(filtro_q)

        # Ordenamiento por fecha (descendente por defecto)
        orden = (self.request.GET.get('orden') or 'desc').strip().lower()
        if orden == 'asc':
            qs = qs.order_by('fecha', 'id')
        else:
            qs = qs.order_by('-fecha', '-id')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hoy = timezone.localdate()
        usuario_db = resolver_usuario_bd(self.request.user)
        empresa_usuario = usuario_db.empresa if usuario_db else None

        cierre_hoy_qs = CierreCaja.objects.filter(fecha=fecha_hoy)
        if empresa_usuario:
            cierre_hoy_qs = cierre_hoy_qs.filter(empresa=empresa_usuario)

        q = (self.request.GET.get('q') or '').strip()
        fecha_filtro = (self.request.GET.get('fecha') or '').strip()
        orden = (self.request.GET.get('orden') or 'desc').strip().lower()

        context.update({
            'cierre_hoy_existe': cierre_hoy_qs.exists(),
            'fecha_hoy': fecha_hoy,
            'q': q,
            'fecha_filtro': fecha_filtro,
            'orden': orden,
        })
        return context
