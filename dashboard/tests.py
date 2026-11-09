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

    def test_rf04_filtro_y_ocultar_periodos_historicos(self):
        """
        [RF-04] Verifica que el dashboard proporcione los controles interactivos
        para filtrar y ocultar períodos históricos cargados en el gráfico de líneas temporales.
        """
        # Asociar un ratio con período específico a la predicción para verificar períodos
        ratio_2025 = RatioFinanciero.objects.create(empresa=self.empresa, periodo='2025-Q4')
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
        ratio_anomalo = RatioFinanciero.objects.create(
            empresa=self.empresa,
            periodo='2026-Q1',
            fecha_calculo=timezone.now(),
            v1_razon_corriente=Decimal("1.50"),
            v2_capital_trabajo_activos=Decimal("0.20"),
            v3_leverage_total=Decimal("8.50"),  # Outlier > 7.0
            v4_roa_operacional=Decimal("0.08"),
            v5_margen_operacional=Decimal("1.40"),  # Outlier > 100%
            v6_rotacion_activos=Decimal("1.20"),
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
        RatioFinanciero.objects.create(
            empresa=self.empresa,
            periodo='2026-Q1',
            fecha_calculo=timezone.now(),
            v1_razon_corriente=Decimal("1.50"),
            v2_capital_trabajo_activos=Decimal("0.20"),
            v3_leverage_total=Decimal("8.50"),
            v4_roa_operacional=Decimal("0.08"),
            v5_margen_operacional=Decimal("1.40"),
            v6_rotacion_activos=Decimal("1.20"),
        )

        total_predicciones_antes = PrediccionRiesgo.objects.filter(empresa=self.empresa).count()

        # POST sin 'forzar_ejecucion'
        response = self.client.post(reverse('dashboard:ejecutar_prediccion'), follow=True)
        self.assertEqual(response.status_code, 200)

        # No debe haberse generado una nueva predicción
        total_predicciones_despues = PrediccionRiesgo.objects.filter(empresa=self.empresa).count()
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
        ratio_anomalo = RatioFinanciero.objects.create(
            empresa=self.empresa,
            periodo='2026-Q1',
            fecha_calculo=timezone.now(),
            v1_razon_corriente=Decimal("1.50"),
            v2_capital_trabajo_activos=Decimal("0.20"),
            v3_leverage_total=Decimal("8.50"),
            v4_roa_operacional=Decimal("0.08"),
            v5_margen_operacional=Decimal("1.40"),
            v6_rotacion_activos=Decimal("1.20"),
        )

        total_predicciones_antes = PrediccionRiesgo.objects.filter(empresa=self.empresa).count()

        # POST con 'forzar_ejecucion=1'
        response = self.client.post(
            reverse('dashboard:ejecutar_prediccion'),
            {'forzar_ejecucion': '1'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Debe haberse generado una nueva predicción
        total_predicciones_despues = PrediccionRiesgo.objects.filter(empresa=self.empresa).count()
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
        RatioFinanciero.objects.create(
            empresa=self.empresa,
            periodo='2026-Q1',
            fecha_calculo=timezone.now(),
            v1_razon_corriente=Decimal("1.80"),
            v2_capital_trabajo_activos=Decimal("0.25"),
            v3_leverage_total=Decimal("0.60"),
            v4_roa_operacional=Decimal("0.10"),
            v5_margen_operacional=Decimal("0.12"),
            v6_rotacion_activos=Decimal("1.20"),
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

        RatioFinanciero.objects.create(
            empresa=self.empresa,
            periodo='2026-Q1',
            fecha_calculo=timezone.now(),
            v1_razon_corriente=Decimal("1.80"),
            v2_capital_trabajo_activos=Decimal("0.25"),
            v3_leverage_total=Decimal("0.60"),
            v4_roa_operacional=Decimal("0.10"),
            v5_margen_operacional=Decimal("0.12"),
            v6_rotacion_activos=Decimal("1.20"),
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
        self.rol_dueno, _ = Rol.objects.get_or_create(id=1, defaults={'nombre': 'Dueño'})
        self.empresa = Empresa.objects.create(rut='76.111.222-3', razon_social='Inversiones Alerta SpA')
        self.usuario_dueno = Usuario.objects.create(
            username='directivo_alerta',
            email='directivo@alerta.cl',
            rol=self.rol_dueno,
            empresa=self.empresa
        )

        # Usuario Django de autenticación
        self.auth_user = User.objects.create_user(
            username='directivo_alerta',
            password='Password123!',
            email='directivo@alerta.cl'
        )

        from moduloETL.models import RatioFinanciero
        from capaAnalitica.models import PrediccionRiesgo

        self.ratio = RatioFinanciero.objects.create(
            empresa=self.empresa,
            periodo='2024-Q4',
            v1_razon_corriente=1.5,
            v2_capital_trabajo_activos=0.2,
            v3_leverage_total=2.0,
            v4_roa_operacional=0.08,
            v5_margen_operacional=0.10,
            v6_rotacion_activos=1.2,
            v7_volatilidad_flujo=0.4,
            fecha_calculo=timezone.now(),
        )

        self.prediccion = PrediccionRiesgo.objects.create(
            ratio=self.ratio,
            empresa=self.empresa,
            score_riesgo=35.0,
            nivel_semaforo='Verde',
            fecha_prediccion=timezone.now(),
            ejecutada_por_usuario=self.usuario_dueno
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
        self.assertContains(response, 'Matriz de Validación Histórica')
        self.assertContains(response, 'alertaTempranaChart')

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


