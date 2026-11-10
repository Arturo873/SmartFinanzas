"""
Pruebas Unitarias y de Integración - Programación Defensiva, Validación de Datos y Manejo de Excepciones.
SmartFinanzas - moduloTransaccional.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User as AuthUser
from django.contrib.messages import get_messages

from usuarios.models import Company, User, Role
from AppWeb.models import UserProfile
from .models import Sale, PaymentMethod, CashRegisterClosure
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
        self.rol_trabajador, _ = Role.objects.get_or_create(name='Trabajador')
        self.rol_dueno, _ = Role.objects.get_or_create(name='Dueño')

        # Empresa
        self.empresa = Company.objects.create(
            business_name="Comercial Test SpA",
            tax_id="76.999.888-1"
        )

        # Usuario Operador (Trabajador)
        self.user_auth = AuthUser.objects.create_user(username='operador', password='password123')
        self.perfil = UserProfile.objects.create(user=self.user_auth, role='Trabajador')
        self.usuario_db = User.objects.create(
            username='operador',
            email='operador@test.cl',
            role=self.rol_trabajador,
            company=self.empresa,
        )
        self.usuario_db.set_password('password123')
        self.usuario_db.save()

        # Métodos de Pago
        self.metodo_efectivo = PaymentMethod.objects.create(
            name="Efectivo",
            commission_percentage=Decimal('0.00'),
            is_active=True,
            company=self.empresa
        )
        self.metodo_tarjeta = PaymentMethod.objects.create(
            name="Tarjeta Débito",
            commission_percentage=Decimal('1.50'),
            is_active=True,
            company=self.empresa
        )
        self.metodo_inactivo = PaymentMethod.objects.create(
            name="Cheque Obsolescente",
            commission_percentage=Decimal('2.00'),
            is_active=False,
            company=self.empresa
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
            'payment_method': self.metodo_tarjeta.pk,
            'gross_total': '10000.00',
            'discount_amount': '1000.00',
        }
        response = self.client.post(self.url_crear_venta, datos, follow=True)

        self.assertEqual(response.status_code, 200)
        venta = Sale.objects.latest('id')
        self.assertEqual(venta.gross_total, Decimal('10000.00'))
        self.assertEqual(venta.discount_amount, Decimal('1000.00'))
        self.assertEqual(venta.charged_total, Decimal('9000.00'))
        # Comisión 1.5% de 9,000 = 135.00
        self.assertEqual(venta.applied_commission, Decimal('135.00'))
        # Ingreso real = 9,000 - 135 = 8,865.00
        self.assertEqual(venta.net_income, Decimal('8865.00'))
        self.assertEqual(venta.company, self.empresa)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("registrada exitosamente" in m for m in mensajes))

    # =========================================================================
    # 2. VALIDACIONES DE NEGOCIO: VALOR 0 O NEGATIVO
    # =========================================================================

    def test_rechazo_venta_con_total_bruto_cero(self):
        """Verifica que NO se procesen ventas con total bruto igual a $0."""
        datos = {
            'payment_method': self.metodo_efectivo.pk,
            'gross_total': '0.00',
            'discount_amount': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("mayor a 0" in m or "ilógica rechazada" in m for m in mensajes))

    def test_rechazo_venta_con_total_bruto_negativo(self):
        """Verifica que NO se procesen ventas con importe negativo."""
        datos = {
            'payment_method': self.metodo_efectivo.pk,
            'gross_total': '-1500.00',
            'discount_amount': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)

        form = response.context['form']
        self.assertTrue(form.has_error('gross_total'))

    def test_rechazo_descuento_negativo(self):
        """Verifica que un descuento negativo sea rechazado."""
        datos = {
            'payment_method': self.metodo_efectivo.pk,
            'gross_total': '5000.00',
            'discount_amount': '-500.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)
        form = response.context['form']
        self.assertTrue(form.has_error('discount_amount'))

    def test_rechazo_descuento_mayor_o_igual_al_total_bruto(self):
        """Verifica que el descuento no consuma el 100% o más de la venta (evitando cobro <= $0)."""
        # Descuento igual al total bruto (cobrado = 0)
        datos = {
            'payment_method': self.metodo_efectivo.pk,
            'gross_total': '5000.00',
            'discount_amount': '5000.00',
        }
        response = self.client.post(self.url_crear_venta, datos)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertTrue(response.context['form'].has_error('discount_amount'))

        # Descuento superior al total bruto (cobrado < 0)
        datos['discount_amount'] = '6000.00'
        response_mayor = self.client.post(self.url_crear_venta, datos)
        self.assertEqual(response_mayor.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertTrue(response_mayor.context['form'].has_error('discount_amount'))

    # =========================================================================
    # 3. VALIDACIONES DE NEGOCIO: VARIABLES VACÍAS O NULAS
    # =========================================================================

    def test_rechazo_variables_vacias_total_bruto_y_metodo(self):
        """Verifica que enviar variables vacías o nulas genere errores amigables y no rompa el sistema."""
        datos_vacios = {
            'payment_method': '',
            'gross_total': '',
            'discount_amount': '',
        }
        response = self.client.post(self.url_crear_venta, datos_vacios)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)
        form = response.context['form']
        self.assertTrue(form.has_error('gross_total'))
        self.assertTrue(form.has_error('payment_method'))

    def test_rechazo_metodo_pago_inactivo(self):
        """Verifica que no se procese una venta con un método de pago deshabilitado."""
        datos = {
            'payment_method': self.metodo_inactivo.pk,
            'gross_total': '20000.00',
            'discount_amount': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)

    # =========================================================================
    # 4. CONDICIONES DE BORDE: CAJA CERRADA
    # =========================================================================

    def test_bloqueo_venta_cuando_caja_del_dia_ya_esta_cerrada(self):
        """No permite registrar ventas sobre un día cuyo arqueo de caja ya fue cerrado."""
        fecha_hoy = timezone.localdate()
        CashRegisterClosure.objects.create(
            date=fecha_hoy,
            status='Cuadrado',
            system_total=Decimal('50000.00'),
            counted_total=Decimal('50000.00'),
            total_discrepancy=Decimal('0.00'),
            company=self.empresa
        )

        datos = {
            'payment_method': self.metodo_efectivo.pk,
            'gross_total': '15000.00',
            'discount_amount': '0.00',
        }
        response = self.client.post(self.url_crear_venta, datos, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)
        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("ya fue cerrada" in m or "Operación bloqueada" in m for m in mensajes))

    # =========================================================================
    # 5. VALIDACIÓN DEFENSIVA EN CIERRE DE CAJA (ARQUEO NEGATIVO Y DESCUADRE)
    # =========================================================================

    def test_cierre_caja_rechaza_arqueo_negativo(self):
        """Verifica que el arqueo de caja no permita conteos físicos negativos."""
        # Usuario Dueño para operar cierre
        user_dueno = AuthUser.objects.create_user(username='duenotest', password='password123')
        UserProfile.objects.create(user=user_dueno, role='Dueño')
        User.objects.create(
            username='duenotest',
            email='dueno@test.cl',
            role=self.rol_dueno,
            company=self.empresa,
        )
        self.client.login(username='duenotest', password='password123')

        datos = {
            'counted_total': '-1000.00',
            'justification': ''
        }
        response = self.client.post(self.url_cierre_caja, datos)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CashRegisterClosure.objects.count(), 0)
        self.assertTrue(response.context['form'].has_error('counted_total'))

    def test_cierre_caja_opcion_a_cuadratura_efectivo_y_tarjetas(self):
        """
        Verifica que según la Opción A:
        El arqueo físico ingresado solo concilie contra el efectivo en gaveta,
        permitiendo que la caja quede 'Cuadrado' sin falsos faltantes por ventas con tarjeta.
        """
        user_dueno2 = AuthUser.objects.create_user(username='dueno_opcion_a', password='password123')
        UserProfile.objects.create(user=user_dueno2, role='Dueño')
        User.objects.create(
            username='dueno_opcion_a',
            email='dueno_a@test.cl',
            role=self.rol_dueno,
            company=self.empresa,
        )
        self.client.login(username='dueno_opcion_a', password='password123')

        # 1. Crear venta en efectivo de $10.000
        Sale.objects.create(
            date=timezone.now(),
            gross_total=Decimal('10000.00'),
            discount_amount=Decimal('0.00'),
            charged_total=Decimal('10000.00'),
            net_income=Decimal('10000.00'),
            applied_commission=Decimal('0.00'),
            payment_method=self.metodo_efectivo,
            company=self.empresa,
            user=self.usuario_db
        )

        # 2. Crear venta con tarjeta de $19.883
        Sale.objects.create(
            date=timezone.now(),
            gross_total=Decimal('20000.00'),
            discount_amount=Decimal('0.00'),
            charged_total=Decimal('20000.00'),
            net_income=Decimal('19883.00'),
            applied_commission=Decimal('117.00'),
            payment_method=self.metodo_tarjeta,
            company=self.empresa,
            user=self.usuario_db
        )

        # 3. El cajero cuenta físicamente $10.000 en la gaveta
        datos = {
            'counted_total': '10000.00',
            'terminos_aceptados': 'on',
            'pos_conciliado': 'on',
            'justification': ''
        }
        response = self.client.post(self.url_cierre_caja, datos, follow=True)
        self.assertEqual(response.status_code, 200)

        cierre = CashRegisterClosure.objects.filter(company=self.empresa).first()
        self.assertIsNotNone(cierre)
        # La caja debe quedar Cuadrada con $0 de descuadre
        self.assertEqual(cierre.status, 'Cuadrado')
        self.assertEqual(cierre.total_discrepancy, Decimal('0.00'))
        # Total sistema consolidado ($10.000 efectivo + $19.883 débito = $29.883)
        self.assertEqual(cierre.system_total, Decimal('29883.00'))
        self.assertEqual(cierre.counted_total, Decimal('29883.00'))
