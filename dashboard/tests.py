"""
Pruebas Unitarias e Integración para la Capa de Presentación Gerencial (Dashboard).
SmartFinanzas.
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User as AuthUser

from usuarios.models import Company, User, Role
from AppWeb.models import UserProfile
from capaAnalitica.models import RiskPrediction
from moduloTransaccional.models import Sale, PaymentMethod
from moduloETL.models import FinancialRatio, FinancialUpload


class DashboardViewTests(TestCase):
    """
    Pruebas de acceso RBAC, consultas de solo lectura y renderizado del Dashboard.
    """

    def setUp(self):
        self.client = Client()

        # Roles del sistema
        self.rol_dueno, _ = Role.objects.get_or_create(name='Dueño')
        self.rol_contador, _ = Role.objects.get_or_create(name='Contador')
        self.rol_trabajador, _ = Role.objects.get_or_create(name='Trabajador')

        # Empresa de prueba
        self.empresa = Company.objects.create(
            business_name="Comercial Norte SpA",
            tax_id="76.123.456-7"
        )

        # Usuario Dueño (Autorizado)
        self.user_auth_dueno = AuthUser.objects.create_user(username='dueno_user', password='password123')
        self.perfil_dueno = UserProfile.objects.create(user=self.user_auth_dueno, role='Dueño')
        self.usuario_db_dueno = User.objects.create(
            username='dueno_user',
            email='dueno@norte.cl',
            role=self.rol_dueno,
            company=self.empresa,
        )
        self.usuario_db_dueno.set_password('password123')
        self.usuario_db_dueno.save()

        # Usuario Trabajador (No Autorizado)
        self.user_auth_trabajador = AuthUser.objects.create_user(username='trabajador_user', password='password123')
        self.perfil_trabajador = UserProfile.objects.create(user=self.user_auth_trabajador, role='Trabajador')
        self.usuario_db_trabajador = User.objects.create(
            username='trabajador_user',
            email='trabajador@norte.cl',
            role=self.rol_trabajador,
            company=self.empresa,
        )
        self.usuario_db_trabajador.set_password('password123')
        self.usuario_db_trabajador.save()

        # Datos de prueba para RiskPrediction (capaAnalitica)
        self.prediccion1 = RiskPrediction.objects.create(
            company=self.empresa,
            prediction_date=timezone.now() - timezone.timedelta(days=2),
            risk_score=Decimal("42.50"),
            traffic_light_level="Amarillo",
            influential_variables=json.dumps([
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

        self.prediccion_reciente = RiskPrediction.objects.create(
            company=self.empresa,
            prediction_date=timezone.now(),
            risk_score=Decimal("78.20"),
            traffic_light_level="Rojo",
            influential_variables=json.dumps([
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
        self.metodo_pago = PaymentMethod.objects.create(name="Efectivo", company=self.empresa)
        self.venta_hoy = Sale.objects.create(
            company=self.empresa,
            date=timezone.now(),
            payment_method=self.metodo_pago,
            gross_total=Decimal("150000.00"),
            charged_total=Decimal("150000.00"),
            net_income=Decimal("148000.00"),
            user=self.usuario_db_dueno,
        )

    def test_acceso_anonimo_redirige_a_login(self):
        """Los usuarios no autenticados deben ser redirigidos al login."""
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('usuarios:login'), response.url)

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

    def test_generar_pdf_predictivo_view_reportlab(self):
        """Verifica que la vista GenerarPDFPredictivoView retorne el informe predictivo a 90 días en PDF."""
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        # Descarga sin parámetros (usa el último período disponible)
        response = self.client.get(reverse('dashboard:generar_pdf_predictivo'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('informe_predictivo_90dias', response['Content-Disposition'])
        self.assertTrue(len(response.content) > 1000)
        self.assertTrue(response.content.startswith(b'%PDF'))

        # Descarga con parámetro de período específico
        response_per = self.client.get(reverse('dashboard:generar_pdf_predictivo') + '?periodo=2024-Q4')
        self.assertEqual(response_per.status_code, 200)
        self.assertEqual(response_per['Content-Type'], 'application/pdf')
        self.assertTrue(response_per.content.startswith(b'%PDF'))

    def test_rf04_filtro_y_ocultar_periodos_historicos(self):
        """
        [RF-04] Verifica que el dashboard proporcione los controles interactivos
        para filtrar y ocultar períodos históricos cargados en el gráfico de líneas temporales.
        """
        # Asociar un ratio con período específico a la predicción para verificar períodos
        ratio_2025 = FinancialRatio.objects.create(company=self.empresa, period='2025-Q4')
        self.prediccion1.ratio = ratio_2025
        self.prediccion1.save()

        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        # 1. Petición inicial sin filtros
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Verificar presencia de datos y períodos en el contexto
        self.assertIn('periodos_disponibles', response.context)
        self.assertIn('chart_puntos_json', response.context)

        periodos = response.context['periodos_disponibles']
        self.assertIn('2025-Q4', periodos)

        puntos_json = json.loads(response.context['chart_puntos_json'])
        self.assertGreaterEqual(len(puntos_json), 2)
        # Al menos uno de los puntos debe corresponder al período 2025-Q4
        periodos_en_puntos = [p['periodo'] for p in puntos_json]
        self.assertIn('2025-Q4', periodos_en_puntos)

        # Verificar elementos de interfaz de usuario para RF-04 en el HTML
        content = response.content.decode('utf-8')
        self.assertIn('dropdownFiltroPeriodos', content)
        self.assertIn('Filtrar / Ocultar Períodos', content)
        self.assertIn('listaCheckboxesPeriodos', content)
        self.assertIn('btnMarcarTodos', content)
        self.assertIn('btnDesmarcarTodos', content)
        self.assertIn('btnRangoUltimos3', content)

        # 2. Petición con filtro de período específico por GET
        response_filtrado = self.client.get(reverse('dashboard:dashboard'), {'periodo': '2025-Q4'})
        self.assertEqual(response_filtrado.status_code, 200)
        puntos_filtrados = json.loads(response_filtrado.context['chart_puntos_json'])
        self.assertEqual(len(puntos_filtrados), 1)
        self.assertEqual(puntos_filtrados[0]['periodo'], '2025-Q4')

    def test_rf10_deteccion_outliers_y_render_modal(self):
        """
        [RF-10] Verifica que cuando existen valores fuera de rango o outliers en los ratios,
        el dashboard identifique las anomalías y renderice el modal de advertencia antes de ejecutar.
        """
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        # Ratio con margen operacional anómalo (> 100%) y leverage extremo
        ratio_anomalo = FinancialRatio.objects.create(
            company=self.empresa,
            period='2026-Q1',
            calculation_date=timezone.now(),
            v1_current_ratio=Decimal("1.50"),
            v2_working_capital_to_assets=Decimal("0.20"),
            v3_total_leverage=Decimal("8.50"),  # Outlier > 7.0
            v4_operating_roa=Decimal("0.08"),
            v5_operating_margin=Decimal("1.40"),  # Outlier > 100%
            v6_asset_turnover=Decimal("1.20"),
        )

        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['tiene_anomalias'])
        self.assertGreaterEqual(response.context['total_anomalias'], 2)

        content = response.content.decode('utf-8')
        self.assertIn('modalAdvertenciaOutliers', content)
        self.assertIn('Valores Anómalos (Outliers) Detectados', content)
        self.assertIn('Forzar Ejecución (Aceptar Alerta)', content)
        self.assertIn('Corregir Datos (Cargar Balance)', content)

    def test_rf10_bloqueo_ejecucion_si_hay_outliers_sin_confirmacion(self):
        """
        [RF-10] Verifica que intentar ejecutar el modelo predictivo con datos anómalos
        sin enviar la confirmación explícita ('forzar_ejecucion') sea bloqueado preventivamente.
        """
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        # Crear ratio con outlier
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2026-Q1',
            calculation_date=timezone.now(),
            v1_current_ratio=Decimal("1.50"),
            v2_working_capital_to_assets=Decimal("0.20"),
            v3_total_leverage=Decimal("8.50"),
            v4_operating_roa=Decimal("0.08"),
            v5_operating_margin=Decimal("1.40"),
            v6_asset_turnover=Decimal("1.20"),
        )

        total_predicciones_antes = RiskPrediction.objects.filter(company=self.empresa).count()

        # POST sin 'forzar_ejecucion'
        response = self.client.post(reverse('dashboard:ejecutar_prediccion'), follow=True)
        self.assertEqual(response.status_code, 200)

        # No debe haberse generado una nueva predicción
        total_predicciones_despues = RiskPrediction.objects.filter(company=self.empresa).count()
        self.assertEqual(total_predicciones_despues, total_predicciones_antes)

        # Mensaje de advertencia debe estar en los mensajes flash
        messages_list = list(response.context['messages'])
        self.assertTrue(any('Advertencia [RF-10]' in str(m) for m in messages_list))

    def test_rf10_forzar_ejecucion_con_confirmacion_explicita(self):
        """
        [RF-10] Verifica que al enviar 'forzar_ejecucion=1' desde el modal de advertencia,
        el sistema proceda con la inferencia del modelo y notifique la aceptación de la alerta.
        """
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        # Crear ratio con outlier
        ratio_anomalo = FinancialRatio.objects.create(
            company=self.empresa,
            period='2026-Q1',
            calculation_date=timezone.now(),
            v1_current_ratio=Decimal("1.50"),
            v2_working_capital_to_assets=Decimal("0.20"),
            v3_total_leverage=Decimal("8.50"),
            v4_operating_roa=Decimal("0.08"),
            v5_operating_margin=Decimal("1.40"),
            v6_asset_turnover=Decimal("1.20"),
        )

        total_predicciones_antes = RiskPrediction.objects.filter(company=self.empresa).count()

        # POST con 'forzar_ejecucion=1'
        response = self.client.post(
            reverse('dashboard:ejecutar_prediccion'),
            {'forzar_ejecucion': '1'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Debe haberse generado una nueva predicción
        total_predicciones_despues = RiskPrediction.objects.filter(company=self.empresa).count()
        self.assertEqual(total_predicciones_despues, total_predicciones_antes + 1)

        # Mensaje de éxito informando que se forzó la ejecución
        messages_list = list(response.context['messages'])
        self.assertTrue(any('Se forzó la ejecución aceptando' in str(m) for m in messages_list))

    def test_rf11_boton_ejecutar_analisis_y_spinner_en_dashboard(self):
        """
        [RF-11] Verifica que el Dashboard renderice el botón 'Ejecutar Análisis'
        y el componente modal con barra/spinner de carga.
        """
        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        # Ratio sin anomalías para habilitar el botón directo
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2026-Q1',
            calculation_date=timezone.now(),
            v1_current_ratio=Decimal("1.80"),
            v2_working_capital_to_assets=Decimal("0.25"),
            v3_total_leverage=Decimal("0.60"),
            v4_operating_roa=Decimal("0.10"),
            v5_operating_margin=Decimal("0.12"),
            v6_asset_turnover=Decimal("1.20"),
        )

        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        # Botón "Ejecutar Análisis"
        self.assertIn('Ejecutar Análisis', content)
        # Spinner y barra de carga animada (RF-11)
        self.assertIn('modalCargaAnalisis', content)
        self.assertIn('spinner-border', content)
        self.assertIn('barraProgresoAnalisis', content)
        self.assertIn('progress-bar-animated', content)

    def test_rf11_ejecutar_analisis_dashboard_tiempo_inferior_10s(self):
        """
        [RF-11] Verifica que la ejecución del análisis predictivo con Random Forest
        tarde estrictamente menos de 10 segundos y redirija con mensaje exitoso.
        """
        import time

        self.client.login(username='dueno_user', password='password123')
        session = self.client.session
        session['usuario_rol'] = 'Dueño'
        session.save()

        FinancialRatio.objects.create(
            company=self.empresa,
            period='2026-Q1',
            calculation_date=timezone.now(),
            v1_current_ratio=Decimal("1.80"),
            v2_working_capital_to_assets=Decimal("0.25"),
            v3_total_leverage=Decimal("0.60"),
            v4_operating_roa=Decimal("0.10"),
            v5_operating_margin=Decimal("0.12"),
            v6_asset_turnover=Decimal("1.20"),
        )

        t_inicio = time.time()
        response = self.client.post(reverse('dashboard:ejecutar_analisis'), follow=False)
        duracion = time.time() - t_inicio

        # Proceso no debe tardar más de 10 segundos
        self.assertLess(duracion, 10.0)

        # Redirige automáticamente al dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:dashboard'))


class AlertaTempranaPredictivoTests(TestCase):
    """
    Pruebas unitarias para el Sistema de Alerta Temprana a 3 Meses (Q_t -> Q_{t+1}),
    cálculo de horizontes temporales, velocidad de cambio (delta) y Dashboard Predictivo.
    """

    def setUp(self):
        from AppWeb.viewsML import calcular_periodo_siguiente, calcular_delta_riesgo
        self.calcular_periodo = calcular_periodo_siguiente
        self.calcular_delta = calcular_delta_riesgo

        # Rol y usuario Dueño
        self.rol_dueno, _ = Role.objects.get_or_create(id=1, defaults={'name': 'Dueño'})
        self.empresa = Company.objects.create(tax_id='76.111.222-3', business_name='Inversiones Alerta SpA')
        self.usuario_dueno = User.objects.create(
            username='directivo_alerta',
            email='directivo@alerta.cl',
            role=self.rol_dueno,
            company=self.empresa
        )

        # Usuario Django de autenticación
        self.auth_user = AuthUser.objects.create_user(
            username='directivo_alerta',
            password='Password123!',
            email='directivo@alerta.cl'
        )

        from moduloETL.models import FinancialRatio
        from capaAnalitica.models import RiskPrediction

        self.ratio = FinancialRatio.objects.create(
            company=self.empresa,
            period='2024-Q4',
            v1_current_ratio=1.5,
            v2_working_capital_to_assets=0.2,
            v3_total_leverage=2.0,
            v4_operating_roa=0.08,
            v5_operating_margin=0.10,
            v6_asset_turnover=1.2,
            v7_cash_flow_volatility=0.4,
            calculation_date=timezone.now(),
        )

        self.prediccion = RiskPrediction.objects.create(
            ratio=self.ratio,
            company=self.empresa,
            risk_score=35.0,
            traffic_light_level='Verde',
            prediction_date=timezone.now(),
            executed_by_user=self.usuario_dueno
        )

    def test_calculo_periodo_siguiente_q4_a_q1(self):
        """Verifica que 2024-Q4 se proyecte hacia 2025-Q1 con 90 días de horizonte."""
        sig, base, dias = self.calcular_periodo('2024-Q4')
        self.assertEqual(sig, '2025-Q1')
        self.assertEqual(base, '2024-Q4')
        self.assertEqual(dias, 90)

    def test_calculo_periodo_siguiente_q1_a_q2(self):
        """Verifica que 2024-Q1 se proyecte hacia 2024-Q2."""
        sig, base, dias = self.calcular_periodo('2024-Q1')
        self.assertEqual(sig, '2024-Q2')
        self.assertEqual(base, '2024-Q1')
        self.assertEqual(dias, 90)

    def test_calculo_delta_riesgo_acelerando(self):
        """Verifica cálculo de variación neta cuando el riesgo aumenta."""
        delta = self.calcular_delta(45.5, 38.0)
        self.assertEqual(delta['direccion'], 'acelerando')
        self.assertEqual(delta['delta'], 7.5)
        self.assertEqual(delta['flecha'], '↑')
        self.assertTrue(delta['es_aumento'])

    def test_calculo_delta_riesgo_reduciendo(self):
        """Verifica cálculo de variación neta cuando el riesgo disminuye."""
        delta = self.calcular_delta(32.0, 42.5)
        self.assertEqual(delta['direccion'], 'reduciendo')
        self.assertEqual(delta['delta'], -10.5)
        self.assertEqual(delta['flecha'], '↓')
        self.assertTrue(delta['es_reduccion'])

    def test_calculo_delta_riesgo_estable(self):
        """Verifica comportamiento cuando no hay variación significativa."""
        delta = self.calcular_delta(25.0, 25.0)
        self.assertEqual(delta['direccion'], 'estable')
        self.assertEqual(delta['delta'], 0.0)

    def test_dashboard_predictivo_view_status_200(self):
        """Verifica que la vista DashboardPredictivoView responda 200 para usuarios autorizados."""
        self.client.force_login(self.auth_user)
        response = self.client.get(reverse('dashboard:dashboard_predictivo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ALERTA TEMPRANA A 3 MESES')
        self.assertContains(response, 'Factores Determinantes de la Proyección')
        self.assertNotContains(response, 'Mini Simulador de Sensibilidad Proactiva')
        self.assertNotContains(response, 'Matriz de Validación Histórica')
        self.assertNotContains(response, 'Velocidad de Cambio')
        self.assertContains(response, 'alertaTempranaChart')
        self.assertContains(response, 'Significado de unidades')
        self.assertContains(response, 'VECES')

    def test_dashboard_predictivo_funciones_grafico(self):
        """
        Verifica que dashboard_predictivo incluya las funciones interactivas del gráfico portadas de dashboard:
        dropdown de filtros, botones de rango rápido, filtro de alertas, contador y datos estructurados.
        """
        self.client.force_login(self.auth_user)
        response = self.client.get(reverse('dashboard:dashboard_predictivo'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Controles de filtrado de períodos
        self.assertIn('dropdownFiltroPeriodos', content)
        self.assertIn('badgePeriodosActivos', content)
        self.assertIn('listaCheckboxesPeriodos', content)
        self.assertIn('btnMarcarTodos', content)
        self.assertIn('btnDesmarcarTodos', content)

        # Botones de rango temporal rápido
        self.assertIn('btnRangoTodos', content)
        self.assertIn('btnRangoUltimos3', content)
        self.assertIn('btnRangoUltimos5', content)

        # Botón de filtro de alertas y contadores
        self.assertIn('btnFiltroAlertas', content)
        self.assertIn('contadorPuntosGrafico', content)
        self.assertIn('btnRestablecerFiltros', content)
        self.assertIn('mensajeSinPeriodos', content)

        # Contenedores de datos JSON seguros
        self.assertIn('id="timeline-puntos-raw"', content)
        self.assertIn('id="timeline-labels-raw"', content)
        self.assertIn('id="timeline-historico-raw"', content)
        self.assertIn('id="timeline-proyectado-raw"', content)
        self.assertNotIn('id="simulador-config-raw"', content)

        # Contexto del backend
        self.assertIn('timeline_puntos_json', response.context)
        puntos = json.loads(response.context['timeline_puntos_json'])
        self.assertTrue(len(puntos) >= 1)
        self.assertEqual(puntos[0]['periodo'], '2024-Q4')
        self.assertTrue(puntos[0]['es_actual'])

    def test_dashboard_general_proyeccion_y_ocultador(self):
        """
        Verifica que la vista general DashboardView incluya la proyección a 90 días (Q_{t+1})
        y el botón interactivo para ocultar o mostrar la predicción.
        """
        self.client.force_login(self.auth_user)
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Botón ocultador de la predicción
        self.assertIn('id="btnToggleProyeccion"', content)
        self.assertIn('Ocultar Predicción', content)

        # Leyenda de la proyección
        self.assertIn('id="leyendaProyeccionItem"', content)
        self.assertIn('Pronóstico 90d', content)

        # Contenedores de proyección en dashboard general
        self.assertIn('id="periodo-proyectado-raw"', content)
        self.assertIn('id="timeline-proyectado-raw"', content)

        # Contexto del backend
        self.assertIn('periodo_proyectado', response.context)
        self.assertIn('score_proyectado', response.context)
        self.assertIn('timeline_proyectado_json', response.context)

    def test_dashboard_predictivo_series_paralelas_y_toggles(self):
        """
        Verifica que el dashboard predictivo incluya la vista limpia con Observados y Proyección a 90 días,
        con sus botones de visibilidad independiente y sin la línea redundante de predicciones brutas.
        """
        self.client.force_login(self.auth_user)
        response = self.client.get(reverse('dashboard:dashboard_predictivo'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Botones de alternancia de series activas
        self.assertIn('id="btnToggleObservados"', content)
        self.assertIn('id="btnToggleProyeccion"', content)
        # La serie morada redundante se eliminó para mantener la curva limpia
        self.assertNotIn('id="btnTogglePredicciones"', content)

        # Contenedores de datos
        self.assertIn('id="timeline-observado-raw"', content)
        self.assertIn('id="timeline-proyectado-raw"', content)

        # Contexto del backend
        self.assertIn('valores_observados', response.context)
        self.assertIn('timeline_observado_json', response.context)
        self.assertIn('timeline_proyectado_json', response.context)

    def test_dashboard_predictivo_historia_completa_sin_recorte(self):
        """
        Verifica que al consultar un período intermedio (ej. 2024-Q2), la vista NO recorte los
        períodos posteriores (2024-Q3, 2024-Q4) para que el botón 'Todos' pueda mostrar toda la historia,
        y que la proyección salga del período consultado (2024-Q2 -> 2024-Q3).
        """
        from moduloETL.models import FinancialRatio

        # Crear trimestres adicionales
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2024-Q1',
            v1_current_ratio=1.8,
            v3_total_leverage=1.2,
            v4_operating_roa=0.09,
            calculation_date=timezone.now(),
        )
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2024-Q2',
            v1_current_ratio=1.4,
            v3_total_leverage=1.8,
            v4_operating_roa=0.06,
            calculation_date=timezone.now(),
        )
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2024-Q3',
            v1_current_ratio=1.3,
            v3_total_leverage=2.1,
            v4_operating_roa=0.05,
            calculation_date=timezone.now(),
        )

        self.client.force_login(self.auth_user)
        # Consultar período intermedio 2024-Q2
        response = self.client.get(reverse('dashboard:dashboard_predictivo') + '?periodo=2024-Q2')
        self.assertEqual(response.status_code, 200)

        # Verificar que todos los trimestres (Q1, Q2, Q3, Q4) estén presentes en timeline_puntos
        puntos = json.loads(response.context['timeline_puntos_json'])
        periodos_presentes = [p['periodo'] for p in puntos]
        self.assertIn('2024-Q1', periodos_presentes)
        self.assertIn('2024-Q2', periodos_presentes)
        self.assertIn('2024-Q3', periodos_presentes)
        self.assertIn('2024-Q4', periodos_presentes)

        # Verificar que 2024-Q2 esté marcado como el actual
        punto_q2 = next(p for p in puntos if p['periodo'] == '2024-Q2')
        self.assertTrue(punto_q2['es_actual'])

        # Verificar que la proyección salga de 2024-Q2 (índice 1) hacia 2024-Q3 (índice 2)
        idx_q2 = periodos_presentes.index('2024-Q2')
        proyectado = json.loads(response.context['timeline_proyectado_json'])
        self.assertIsNotNone(proyectado[idx_q2])
        self.assertIsNotNone(proyectado[idx_q2 + 1])
        # Los otros puntos históricos antes y después deben ser None
        self.assertIsNone(proyectado[0]) # Q1
        self.assertIsNone(proyectado[idx_q2 + 2]) # Q4

    def test_calcular_score_observado(self):
        """
        Verifica el cálculo de insolvencia contable observado a partir de la
        formulación clásica de Edward Altman (1983) para empresas no manufactureras
        y mercados emergentes (Z''-Score).
        """
        from dashboard.views import calcular_score_observado, calcular_z_score_altman_1983
        from moduloETL.models import FinancialRatio

        # Caso solvente (alta liquidez, bajo endeudamiento)
        r_solvente = FinancialRatio(
            v1_current_ratio=2.2,
            v2_working_capital_to_assets=0.3,
            v3_total_leverage=0.8,
            v4_operating_roa=0.12,
        )
        z_solvente = calcular_z_score_altman_1983(r_solvente)
        self.assertGreaterEqual(z_solvente, 2.60)  # Zona Segura de Altman
        score_solvente = calcular_score_observado(r_solvente)
        self.assertLessEqual(score_solvente, 35.0)  # Zona Verde

        # Caso crítico (baja liquidez, alto endeudamiento, ROA negativo)
        r_critico = FinancialRatio(
            v1_current_ratio=0.6,
            v2_working_capital_to_assets=-0.2,
            v3_total_leverage=5.5,
            v4_operating_roa=-0.08,
        )
        z_critico = calcular_z_score_altman_1983(r_critico)
        self.assertLess(z_critico, 1.10)  # Zona de Quiebra de Altman
        score_critico = calcular_score_observado(r_critico)
        self.assertGreater(score_critico, 70.0)  # Zona Roja Crítica

    def test_dashboard_ver_periodo_preserva_todos_para_grafico_y_shap_ancho_completo(self):
        """
        Verifica que al abrir /dashboard/?periodo=... (botón VER de Ratios Financieros):
        1. timeline_puntos_json conserve toda la historia para que el botón 'Todos' muestre todos los períodos.
        2. timeline_proyectado_json y timeline_labels se alineen con el período seleccionado.
        3. Explicabilidad SHAP ocupe todo el ancho (col-12 sin col-lg-8/col-xl-9).
        4. El tooltip del gráfico filtre el ancla duplicada del dataset proyectado.
        """
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2024-Q2',
            v1_current_ratio=1.6,
            v2_working_capital_to_assets=0.22,
            v3_total_leverage=1.4,
            v4_operating_roa=0.07,
            calculation_date=timezone.now(),
        )
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2024-Q3',
            v1_current_ratio=1.4,
            v2_working_capital_to_assets=0.18,
            v3_total_leverage=1.7,
            v4_operating_roa=0.05,
            calculation_date=timezone.now(),
        )

        self.client.force_login(self.auth_user)
        response = self.client.get(reverse('dashboard:dashboard'), {'periodo': '2024-Q2'})
        self.assertEqual(response.status_code, 200)

        puntos_filtrados = json.loads(response.context['chart_puntos_json'])
        self.assertEqual(len(puntos_filtrados), 1)
        self.assertEqual(puntos_filtrados[0]['periodo'], '2024-Q2')

        puntos_completos = json.loads(response.context['timeline_puntos_json'])
        periodos_completos = [p['periodo'] for p in puntos_completos]
        self.assertIn('2024-Q2', periodos_completos)
        self.assertIn('2024-Q3', periodos_completos)
        self.assertIn('2024-Q4', periodos_completos)

        punto_q2 = next(p for p in puntos_completos if p['periodo'] == '2024-Q2')
        self.assertTrue(punto_q2['es_actual'])

        labels = json.loads(response.context['timeline_labels_json'])
        self.assertEqual(labels[-1], '2025-Q1')

        idx_q2 = periodos_completos.index('2024-Q2')
        proyectado = json.loads(response.context['timeline_proyectado_json'])
        self.assertIsNotNone(proyectado[idx_q2])
        self.assertIsNotNone(proyectado[idx_q2 + 1])

        content = response.content.decode('utf-8')
        self.assertNotIn('col-12 col-lg-8 col-xl-9', content)
        self.assertIn('<!-- Explicabilidad SHAP del Diagnóstico (Ancho completo) -->', content)
        self.assertIn("document.getElementById('timeline-puntos-raw')", content)
        self.assertIn('destIdxActual', content)
        self.assertNotIn('| Altman Z', content)

    def test_dashboard_solo_ratios_sin_prediccion_no_falla(self):
        """
        Verifica que cuando la empresa tiene FinancialRatio pero aún no tiene RiskPrediction,
        DashboardView no lance UnboundLocalError por ultimo_ratio.
        """
        RiskPrediction.objects.filter(company=self.empresa).delete()
        FinancialRatio.objects.filter(company=self.empresa).delete()
        FinancialRatio.objects.create(
            company=self.empresa,
            period='2025-Q1',
            v1_current_ratio=1.7,
            v2_working_capital_to_assets=0.25,
            v3_total_leverage=1.1,
            v4_operating_roa=0.09,
            calculation_date=timezone.now(),
        )

        self.client.force_login(self.auth_user)
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        puntos = json.loads(response.context['timeline_puntos_json'])
        self.assertEqual(len(puntos), 1)
        self.assertTrue(puntos[0]['es_actual'])




