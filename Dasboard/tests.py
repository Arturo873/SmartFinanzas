"""
Pruebas Unitarias e Integración para la Capa de Presentación Gerencial (Dashboard).
SmartFinanzas.
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from usuarios.models import Empresa, Usuario, Rol
from AppWeb.models import PerfilUsuario
from capaAnalitica.models import PrediccionRiesgo
from moduloTransaccional.models import Venta, MetodoPago
from moduloETL.models import RatioFinanciero, CargaFinanciera


class DashboardViewTests(TestCase):
    """
    Pruebas de acceso RBAC, consultas de solo lectura y renderizado del Dashboard.
    """

    def setUp(self):
        self.client = Client()

        # Roles del sistema
        self.rol_dueno, _ = Rol.objects.get_or_create(nombre='Dueño')
        self.rol_contador, _ = Rol.objects.get_or_create(nombre='Contador')
        self.rol_trabajador, _ = Rol.objects.get_or_create(nombre='Trabajador')

        # Empresa de prueba
        self.empresa = Empresa.objects.create(
            razon_social="Comercial Norte SpA",
            rut="76.123.456-7"
        )

        # Usuario Dueño (Autorizado)
        self.user_auth_dueno = User.objects.create_user(username='dueno_user', password='password123')
        self.perfil_dueno = PerfilUsuario.objects.create(user=self.user_auth_dueno, rol='Dueño')
        self.usuario_db_dueno = Usuario.objects.create(
            username='dueno_user',
            email='dueno@norte.cl',
            rol=self.rol_dueno,
            empresa=self.empresa,
        )
        self.usuario_db_dueno.set_password('password123')
        self.usuario_db_dueno.save()

        # Usuario Trabajador (No Autorizado)
        self.user_auth_trabajador = User.objects.create_user(username='trabajador_user', password='password123')
        self.perfil_trabajador = PerfilUsuario.objects.create(user=self.user_auth_trabajador, rol='Trabajador')
        self.usuario_db_trabajador = Usuario.objects.create(
            username='trabajador_user',
            email='trabajador@norte.cl',
            rol=self.rol_trabajador,
            empresa=self.empresa,
        )
        self.usuario_db_trabajador.set_password('password123')
        self.usuario_db_trabajador.save()

        # Datos de prueba para PrediccionRiesgo (capaAnalitica)
        self.prediccion1 = PrediccionRiesgo.objects.create(
            empresa=self.empresa,
            fecha_prediccion=timezone.now() - timezone.timedelta(days=2),
            score_riesgo=Decimal("42.50"),
            nivel_semaforo="Amarillo",
            variables_influyentes=json.dumps([
                {
                    'nombre': 'Margen Operacional',
                    'impacto_pct': 12.5,
                    'impacto_abs': 12.5,
                    'texto': 'La caída del Margen Operacional aportó un +12.5% al riesgo',
                    'valor': 0.05,
                    'unidad': '%'
                }
            ]),
        )

        self.prediccion_reciente = PrediccionRiesgo.objects.create(
            empresa=self.empresa,
            fecha_prediccion=timezone.now(),
            score_riesgo=Decimal("78.20"),
            nivel_semaforo="Rojo",
            variables_influyentes=json.dumps([
                {
                    'codigo': 'X5',
                    'nombre': 'Margen Operacional',
                    'impacto_pct': 15.0,
                    'impacto_abs': 15.0,
                    'texto': 'La caída del Margen Operacional aportó un +15% al riesgo',
                    'valor': 0.02,
                    'unidad': '%'
                },
                {
                    'codigo': 'X2',
                    'nombre': 'Capital de Trabajo sobre Activos',
                    'impacto_pct': 12.4,
                    'impacto_abs': 12.4,
                    'texto': 'El Ratio de Capital de Trabajo disminuyó drásticamente, incrementando el riesgo',
                    'valor': -0.10,
                    'unidad': '%'
                },
                {
                    'codigo': 'X3',
                    'nombre': 'Leverage Total',
                    'impacto_pct': 8.5,
                    'impacto_abs': 8.5,
                    'texto': 'El elevado Leverage Total presiona la solvencia financiera',
                    'valor': 4.5,
                    'unidad': 'x'
                }
            ]),
        )

        # Transacción de Venta (moduloTransaccional / app_caja) del día actual
        self.metodo_pago = MetodoPago.objects.create(nombre="Efectivo", empresa=self.empresa)
        self.venta_hoy = Venta.objects.create(
            empresa=self.empresa,
            fecha=timezone.now(),
            metodo_pago=self.metodo_pago,
            total_bruto=Decimal("150000.00"),
            total_cobrado=Decimal("150000.00"),
            ingreso_real=Decimal("148000.00"),
            usuario=self.usuario_db_dueno,
        )

    def test_acceso_anonimo_redirige_a_login(self):
        """Los usuarios no autenticados deben ser redirigidos al login."""
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_acceso_rol_no_autorizado_es_bloqueado(self):
        """Los usuarios con rol Trabajador no deben tener acceso al Dashboard gerencial."""
        self.client.login(username='trabajador_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Trabajador'
        session.save()

        response = self.client.get(reverse('dashboard:dashboard'))
        # Redirige con mensaje de error a principal
        self.assertEqual(response.status_code, 302)

    def test_acceso_rol_dueno_permitido(self):
        """El Dueño puede acceder al Dashboard con éxito."""
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_datos_contexto_dashboard(self):
        """Verifica que el contexto contenga la última predicción, el score, SHAP y ventas del día."""
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Última Predicción (Score 78.20, Nivel Rojo)
        self.assertEqual(response.context['score'], 78.20)
        self.assertEqual(response.context['nivel'], 'Rojo')

        # SHAP Top 3
        top3 = response.context['top_3_variables']
        self.assertEqual(len(top3), 3)
        self.assertEqual(top3[0]['nombre'], 'Margen Operacional')

        # Ingreso Real del día actual sumado de Venta
        self.assertEqual(response.context['ingreso_real_hoy'], Decimal("148000.00"))
        self.assertEqual(response.context['total_ventas_hoy'], 1)

        # Datos para Chart.js
        fechas_json = json.loads(response.context['chart_fechas_json'])
        scores_json = json.loads(response.context['chart_scores_json'])
        self.assertEqual(len(scores_json), 2)
        self.assertIn(78.2, scores_json)

    def test_renderizado_elementos_ui(self):
        """Verifica la presencia del semáforo con clase bg-danger, el canvas Chart.js y el botón PDF."""
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        response = self.client.get(reverse('dashboard:dashboard'))
        content = response.content.decode('utf-8')

        # Sección 1: Semáforo y score con clase condicional
        self.assertIn('bg-danger', content)
        self.assertIn('78.2%', content)

        # Sección 2: Panel de explicabilidad SHAP
        self.assertIn('Margen Operacional', content)
        self.assertIn('Capital de Trabajo sobre Activos', content)

        # Sección 3: Canvas de Chart.js
        self.assertIn('<canvas id="riesgoChart"', content)

        # Sección 4: Botón de exportación PDF
        self.assertIn('Descargar Informe Ejecutivo', content)

    def test_generar_pdf_view_reportlab(self):
        """Verifica que la vista GenerarPDFView retorne un documento PDF válido."""
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        response = self.client.get(reverse('dashboard:generar_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertTrue(len(response.content) > 1000)
        # Magic bytes de un archivo PDF (%PDF)
        self.assertTrue(response.content.startswith(b'%PDF'))
