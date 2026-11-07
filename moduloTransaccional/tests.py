"""
Pruebas Unitarias y de Integración - Programación Defensiva, Validación de Datos y Manejo de Excepciones.
SmartFinanzas - moduloTransaccional.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from usuarios.models import Empresa, Usuario, Rol
from AppWeb.models import PerfilUsuario
from .models import Venta, MetodoPago, CierreCaja
from .forms import VentaForm, CierreCajaForm


class ModuloTransaccionalDefensiveTests(TestCase):
    """
    Suite de pruebas para validar los principios de:
    1. Validaciones de Negocio (monto > 0, cobro > 0, variables nulas/vacías, caja cerrada).
    2. Manejo de Excepciones (cálculos de comisiones, división segura, transaccionalidad).
    3. Generación de Alertas Amigables y Descriptivas (causa y solución).
    """

    def setUp(self):
        self.client = Client()

        # Roles
        self.rol_trabajador, _ = Rol.objects.get_or_create(nombre='Trabajador')
        self.rol_dueno, _ = Rol.objects.get_or_create(nombre='Dueño')

        # Empresa
        self.empresa = Empresa.objects.create(
            razon_social="Comercial Test SpA",
            rut="76.999.888-1"
        )

        # Usuario Operador (Trabajador)
        self.user_auth = User.objects.create_user(username='operador', password='password123')
        self.perfil = PerfilUsuario.objects.create(user=self.user_auth, rol='Trabajador')
        self.usuario_db = Usuario.objects.create(
            username='operador',
            email='operador@test.cl',
            rol=self.rol_trabajador,
            empresa=self.empresa,
        )
        self.usuario_db.set_password('password123')
        self.usuario_db.save()

        # Métodos de Pago
        self.metodo_efectivo = MetodoPago.objects.create(
            nombre="Efectivo",
            comision_porcentaje=Decimal('0.00'),
            activo=True,
            empresa=self.empresa
        )
        self.metodo_tarjeta = MetodoPago.objects.create(
            nombre="Tarjeta Débito",
            comision_porcentaje=Decimal('1.50'),
            activo=True,
            empresa=self.empresa
        )
        self.metodo_inactivo = MetodoPago.objects.create(
            nombre="Cheque Obsolescente",
            comision_porcentaje=Decimal('2.00'),
            activo=False,
            empresa=self.empresa
        )

        self.url_crear_venta = reverse('moduloTransaccional:venta_crear')
        self.url_cierre_caja = reverse('moduloTransaccional:cierre_caja')

        # Iniciar sesión con el usuario trabajador
        self.client.login(username='operador', password='password123')

    # =========================================================================
    # 1. PRUEBAS DE VENTA EXITOSA Y CÁLCULOS PROTEGIDOS
    # =========================================================================

    def test_registro_venta_valida_con_calculo_financiero(self):
        """Una venta con datos correctos calcula cobrado, comisión e ingreso real de forma precisa."""
        datos = {
            'metodo_pago': self.metodo_tarjeta.pk,
            'total_bruto': '10000.00',
            'descuento_monto': '1000.00',
        }
        response = self.client.post(self.url_crear_venta, datos, follow=True)

        self.assertEqual(response.status_code, 200)
        venta = Venta.objects.latest('id')
        self.assertEqual(venta.total_bruto, Decimal('10000.00'))
        self.assertEqual(venta.descuento_monto, Decimal('1000.00'))
        self.assertEqual(venta.total_cobrado, Decimal('9000.00'))
        # Comisión 1.5% de 9,000 = 135.00
        self.assertEqual(venta.comision_aplicada, Decimal('135.00'))
        # Ingreso real = 9,000 - 135 = 8,865.00
        self.assertEqual(venta.ingreso_real, Decimal('8865.00'))
        self.assertEqual(venta.empresa, self.empresa)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("registrada exitosamente" in m for m in mensajes))

    # =========================================================================
    # 2. VALIDACIONES DE NEGOCIO: VALOR 0 O NEGATIVO
    # =========================================================================

    def test_rechazo_venta_con_total_bruto_cero(self):
        """Verifica que NO se procesen ventas con total bruto igual a $0."""
        datos = {
            'metodo_pago': self.metodo_efectivo.pk,
            'total_bruto': '0.00',
            'descuento_monto': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("mayor a 0" in m or "ilógica rechazada" in m for m in mensajes))

    def test_rechazo_venta_con_total_bruto_negativo(self):
        """Verifica que NO se procesen ventas con importe negativo."""
        datos = {
            'metodo_pago': self.metodo_efectivo.pk,
            'total_bruto': '-1500.00',
            'descuento_monto': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)

        form = response.context['form']
        self.assertTrue(form.has_error('total_bruto'))

    def test_rechazo_descuento_negativo(self):
        """Verifica que un descuento negativo sea rechazado."""
        datos = {
            'metodo_pago': self.metodo_efectivo.pk,
            'total_bruto': '5000.00',
            'descuento_monto': '-500.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)
        form = response.context['form']
        self.assertTrue(form.has_error('descuento_monto'))

    def test_rechazo_descuento_mayor_o_igual_al_total_bruto(self):
        """Verifica que el descuento no consuma el 100% o más de la venta (evitando cobro <= $0)."""
        # Descuento igual al total bruto (cobrado = 0)
        datos = {
            'metodo_pago': self.metodo_efectivo.pk,
            'total_bruto': '5000.00',
            'descuento_monto': '5000.00',
        }
        response = self.client.post(self.url_crear_venta, datos)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)
        self.assertTrue(response.context['form'].has_error('descuento_monto'))

        # Descuento superior al total bruto (cobrado < 0)
        datos['descuento_monto'] = '6000.00'
        response_mayor = self.client.post(self.url_crear_venta, datos)
        self.assertEqual(response_mayor.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)
        self.assertTrue(response_mayor.context['form'].has_error('descuento_monto'))

    # =========================================================================
    # 3. VALIDACIONES DE NEGOCIO: VARIABLES VACÍAS O NULAS
    # =========================================================================

    def test_rechazo_variables_vacias_total_bruto_y_metodo(self):
        """Verifica que enviar variables vacías o nulas genere errores amigables y no rompa el sistema."""
        datos_vacios = {
            'metodo_pago': '',
            'total_bruto': '',
            'descuento_monto': '',
        }
        response = self.client.post(self.url_crear_venta, datos_vacios)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)
        form = response.context['form']
        self.assertTrue(form.has_error('total_bruto'))
        self.assertTrue(form.has_error('metodo_pago'))

    def test_rechazo_metodo_pago_inactivo(self):
        """Verifica que no se procese una venta con un método de pago deshabilitado."""
        datos = {
            'metodo_pago': self.metodo_inactivo.pk,
            'total_bruto': '20000.00',
            'descuento_monto': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)

    # =========================================================================
    # 4. CONDICIONES DE BORDE: CAJA CERRADA
    # =========================================================================

    def test_bloqueo_venta_cuando_caja_del_dia_ya_esta_cerrada(self):
        """No permite registrar ventas sobre un día cuyo arqueo de caja ya fue cerrado."""
        fecha_hoy = timezone.localdate()
        CierreCaja.objects.create(
            fecha=fecha_hoy,
            estado='Cuadrado',
            total_sistema=Decimal('50000.00'),
            total_arqueo=Decimal('50000.00'),
            descuadre_total=Decimal('0.00'),
            empresa=self.empresa
        )

        datos = {
            'metodo_pago': self.metodo_efectivo.pk,
            'total_bruto': '15000.00',
            'descuento_monto': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 0)
        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("ya fue cerrada" in m or "Operación bloqueada" in m for m in mensajes))

    # =========================================================================
    # 5. VALIDACIÓN DEFENSIVA EN CIERRE DE CAJA (ARQUEO NEGATIVO Y DESCUADRE)
    # =========================================================================

    def test_cierre_caja_rechaza_arqueo_negativo(self):
        """Verifica que el arqueo de caja no permita conteos físicos negativos."""
        # Usuario Dueño para operar cierre
        user_dueno = User.objects.create_user(username='duenotest', password='password123')
        PerfilUsuario.objects.create(user=user_dueno, rol='Dueño')
        Usuario.objects.create(
            username='duenotest',
            email='dueno@test.cl',
            rol=self.rol_dueno,
            empresa=self.empresa,
        )
        self.client.login(username='duenotest', password='password123')

        datos = {
            'total_arqueo': '-1000.00',
            'justificacion': ''
        }
        response = self.client.post(self.url_cierre_caja, datos)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CierreCaja.objects.count(), 0)
        self.assertTrue(response.context['form'].has_error('total_arqueo'))
