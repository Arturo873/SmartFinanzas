"""
Suite de Pruebas Unitarias y de Integración para el Módulo ETL de SmartFinanzas.
Incluye validación de aislamiento por empresa (multi-tenant).
"""

import io
import os
import pandas as pd
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CargaFinanciera, RatioFinanciero
from .forms import CargaArchivoForm
from .services import (
    COLUMNAS_PLANTILLA,
    extraer_dataframe_desde_archivo,
    validar_estructura_y_consistencia,
    calcular_indicadores_completos,
    procesar_e_ingestar_balance,
    limpiar_archivos_y_estado,
    generar_plantilla_ejemplo_csv,
    calcular_zem_altman,
    detectar_anomalias_financieras,
)
from usuarios.models import Usuario, Empresa, Rol
from AppWeb.models import PerfilUsuario, EstadoCarga


FILA_BALANCE_SANO = {
    'Id_Empresa': '76.123.456-7',
    'Periodo': '2025-Q4',
    'Activo_Circulante': 500.0,
    'Pasivo_Circulante': 250.0,
    'Efectivo_Equivalentes': 100.0,
    'Inventarios': 150.0,
    'Activo_Total': 1000.0,
    'Pasivo_Total': 400.0,
    'Patrimonio_Neto': 600.0,
    'Utilidad_Neta': 60.0,
    'Ingresos_Netos': 1200.0,
    'EBIT': 90.0,
    'Utilidades_Retenidas': 200.0,
}


class ETLServicesTests(TestCase):
    """Pruebas unitarias para las funciones del servicio ETL."""

    def test_extraer_csv_delimitador_coma_y_punto_coma(self):
        df_base = pd.DataFrame([FILA_BALANCE_SANO])
        csv_punto_coma = df_base.to_csv(index=False, sep=';').encode('utf-8')
        archivo_pc = SimpleUploadedFile('test.csv', csv_punto_coma, content_type='text/csv')
        df_out, errs = extraer_dataframe_desde_archivo(archivo_pc)
        self.assertEqual(len(errs), 0)
        self.assertIsNotNone(df_out)
        self.assertEqual(len(df_out), 1)

        csv_coma = df_base.to_csv(index=False, sep=',').encode('utf-8')
        archivo_c = SimpleUploadedFile('test_coma.csv', csv_coma, content_type='text/csv')
        df_out2, errs2 = extraer_dataframe_desde_archivo(archivo_c)
        self.assertEqual(len(errs2), 0)
        self.assertEqual(len(df_out2), 1)

    def test_rechazar_archivo_formato_no_soportado(self):
        archivo_txt = SimpleUploadedFile('prueba.txt', b'datos...', content_type='text/plain')
        df_out, errs = extraer_dataframe_desde_archivo(archivo_txt)
        self.assertIsNone(df_out)
        self.assertTrue(any('Formato no soportado' in e for e in errs))

    def test_rechazar_columnas_faltantes(self):
        fila_incompleta = {k: v for k, v in FILA_BALANCE_SANO.items() if k not in ('EBIT', 'Ingresos_Netos')}
        df = pd.DataFrame([fila_incompleta])
        valido, errs, _ = validar_estructura_y_consistencia(df)
        self.assertFalse(valido)
        self.assertTrue(any('Columnas faltantes' in e for e in errs))

    def test_rechazar_celdas_nulas(self):
        fila_con_nulo = {**FILA_BALANCE_SANO, 'Activo_Circulante': None}
        df = pd.DataFrame([fila_con_nulo])
        valido, errs, _ = validar_estructura_y_consistencia(df)
        self.assertFalse(valido)
        self.assertTrue(any('celda(s) vacía(s)' in e for e in errs))

    def test_rechazar_descuadre_contable_patrimonial(self):
        fila_descuadrada = {**FILA_BALANCE_SANO, 'Patrimonio_Neto': 800.0}
        df = pd.DataFrame([fila_descuadrada])
        valido, errs, _ = validar_estructura_y_consistencia(df)
        self.assertFalse(valido)
        self.assertTrue(any('Descuadre contable detectado' in e for e in errs))

    def test_rechazar_activo_circulante_mayor_que_activo_total(self):
        fila_invalida = {**FILA_BALANCE_SANO, 'Activo_Circulante': 1500.0}
        df = pd.DataFrame([fila_invalida])
        valido, errs, _ = validar_estructura_y_consistencia(df)
        self.assertFalse(valido)
        self.assertTrue(any('Inconsistencia contable' in e for e in errs))

    def test_calculo_indicadores_exactos(self):
        indicadores = calcular_indicadores_completos(FILA_BALANCE_SANO)
        self.assertAlmostEqual(indicadores['v1_razon_corriente'], 2.0)
        self.assertAlmostEqual(indicadores['v2_capital_trabajo_activos'], 0.25)
        self.assertAlmostEqual(indicadores['v3_leverage_total'], round(400 / 600, 4))
        self.assertAlmostEqual(indicadores['v4_roa_operacional'], 0.09)
        self.assertAlmostEqual(indicadores['v5_margen_operacional'], 0.075)
        self.assertAlmostEqual(indicadores['v6_rotacion_activos'], 1.2)
        altman_calculado = calcular_zem_altman(FILA_BALANCE_SANO)
        self.assertAlmostEqual(indicadores['ref_z_altman'], altman_calculado)

    def test_rf10_detectar_anomalias_financieras_outliers(self):
        """[RF-10] Verifica detección de outliers y cuentas con signos inválidos."""
        # 1. Caso sin anomalías
        ratio_sano = RatioFinanciero(
            v1_razon_corriente=Decimal("1.50"),
            v2_capital_trabajo_activos=Decimal("0.20"),
            v3_leverage_total=Decimal("0.80"),
            v4_roa_operacional=Decimal("0.10"),
            v5_margen_operacional=Decimal("0.12"),
            v6_rotacion_activos=Decimal("1.10"),
        )
        anomalias_sanas = detectar_anomalias_financieras(ratio_sano)
        self.assertEqual(len(anomalias_sanas), 0)

        # 2. Caso con ratio outlier extremo (Margen Operacional > 100% y Leverage > 7.0)
        ratio_outlier = RatioFinanciero(
            v1_razon_corriente=Decimal("9.50"),
            v3_leverage_total=Decimal("8.20"),
            v5_margen_operacional=Decimal("1.50"),
        )
        anomalias = detectar_anomalias_financieras(ratio_outlier)
        self.assertGreaterEqual(len(anomalias), 3)
        campos = [a['campo'] for a in anomalias]
        self.assertIn('Razón Corriente (V1)', campos)
        self.assertIn('Leverage Total (V3)', campos)
        self.assertIn('Margen Operacional (V5)', campos)

        # 3. Caso con carga con cuenta negativa (Efectivo negativo)
        carga_invalida = CargaFinanciera(
            efectivo_equivalentes=Decimal("-50000"),
            activo_total=Decimal("1000000"),
        )
        anomalias_carga = detectar_anomalias_financieras(carga_invalida)
        self.assertTrue(any(a['campo'] == 'Efectivo y Equivalentes' for a in anomalias_carga))

    def test_generar_plantilla_descargable(self):
        csv_bytes = generar_plantilla_ejemplo_csv()
        self.assertIsInstance(csv_bytes, bytes)
        texto = csv_bytes.decode('utf-8')
        for col in COLUMNAS_PLANTILLA:
            self.assertIn(col, texto)


class ETLIntegrationAndViewsTests(TestCase):
    """Pruebas de integración para las Vistas y aislamiento multi-tenant por empresa."""

    def setUp(self):
        # Roles
        self.rol_contador, _ = Rol.objects.get_or_create(nombre='Contador', defaults={'descripcion': 'Rol Contador'})
        self.rol_dueno, _ = Rol.objects.get_or_create(nombre='Dueño', defaults={'descripcion': 'Rol Dueño'})

        # Empresa 1
        self.empresa1 = Empresa.objects.create(
            razon_social='Nstock Importaciones',
            rut='76.123.456-7'
        )

        # Empresa 2 (para probar aislamiento)
        self.empresa2 = Empresa.objects.create(
            razon_social='Empresa Externa SpA',
            rut='99.888.777-6'
        )

        # Usuario Contador de Empresa 1
        self.auth_contador = User.objects.create_user(username='contador_test', password='password123')
        PerfilUsuario.objects.create(user=self.auth_contador, rol='Contador')
        self.usuario_db = Usuario.objects.create(
            username='contador_test',
            email='contador@test.cl',
            rol=self.rol_contador,
            empresa=self.empresa1
        )
        self.usuario_db.set_password('password123')
        self.usuario_db.save()

        # Usuario de Empresa 2
        self.auth_user2 = User.objects.create_user(username='user2_test', password='password123')
        PerfilUsuario.objects.create(user=self.auth_user2, rol='Dueño')
        self.usuario2_db = Usuario.objects.create(
            username='user2_test',
            email='user2@test.cl',
            rol=self.rol_dueno,
            empresa=self.empresa2
        )
        self.usuario2_db.set_password('password123')
        self.usuario2_db.save()

    def tearDown(self):
        limpiar_archivos_y_estado()

    def _generar_archivo_post(self, filas):
        csv_content = pd.DataFrame(filas).to_csv(index=False, sep=';').encode('utf-8')
        return SimpleUploadedFile('balance_test.csv', csv_content, content_type='text/csv')

    def test_carga_datos_vista_get(self):
        self.client.force_login(self.auth_contador)
        resp = self.client.get(reverse('moduloETL:carga_datos'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Módulo ETL: Carga de Estados')
        self.assertContains(resp, 'Nstock Importaciones')
        # Verificar que NO existe selector de empresas en el formulario
        self.assertNotContains(resp, 'name="empresa"')

    def test_carga_datos_vista_post_asocia_empresa_usuario(self):
        self.client.force_login(self.auth_contador)
        archivo = self._generar_archivo_post([FILA_BALANCE_SANO])

        # Se envía SIN especificar empresa; el backend la asigna automáticamente del usuario
        resp = self.client.post(
            reverse('moduloETL:carga_datos'),
            {
                'tipo_documento': 'Balance General',
                'archivo_datos': archivo,
            },
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(CargaFinanciera.objects.count(), 1)
        self.assertEqual(RatioFinanciero.objects.count(), 1)

        carga = CargaFinanciera.objects.first()
        self.assertEqual(carga.empresa, self.empresa1)
        self.assertEqual(carga.periodo, '2025-Q4')

        ratio = RatioFinanciero.objects.first()
        self.assertEqual(ratio.empresa, self.empresa1)

    def test_aislamiento_multi_empresa_ratios_y_cargas(self):
        # 1. Cargar datos para Empresa 1
        self.client.force_login(self.auth_contador)
        archivo = self._generar_archivo_post([FILA_BALANCE_SANO])
        self.client.post(
            reverse('moduloETL:carga_datos'),
            {'tipo_documento': 'Balance General', 'archivo_datos': archivo}
        )

        # 2. Iniciar sesión como Usuario de Empresa 2
        self.client.force_login(self.auth_user2)

        # La vista de ratios de Empresa 2 NO debe ver los ratios de Empresa 1
        resp_ratios = self.client.get(reverse('moduloETL:ratios_financieros'))
        self.assertEqual(resp_ratios.status_code, 200)
        self.assertEqual(len(resp_ratios.context['ratios']), 0)
        self.assertContains(resp_ratios, 'No hay ratios calculados para tu empresa')

        # La vista de historial de Empresa 2 NO debe ver las cargas de Empresa 1
        resp_historial = self.client.get(reverse('moduloETL:historial_cargas'))
        self.assertEqual(resp_historial.status_code, 200)
        self.assertEqual(len(resp_historial.context['cargas']), 0)
        self.assertContains(resp_historial, 'No hay cargas contables registradas para tu empresa')

    def test_carga_datos_vista_post_rechaza_descuadre(self):
        self.client.force_login(self.auth_contador)
        fila_descuadrada = {**FILA_BALANCE_SANO, 'Pasivo_Total': 900.0}
        archivo = self._generar_archivo_post([fila_descuadrada])

        resp = self.client.post(
            reverse('moduloETL:carga_datos'),
            {
                'tipo_documento': 'Balance General',
                'archivo_datos': archivo,
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(CargaFinanciera.objects.count(), 0)
        self.assertEqual(RatioFinanciero.objects.count(), 0)

    def test_descargar_plantilla(self):
        self.client.force_login(self.auth_contador)
        resp = self.client.get(reverse('moduloETL:descargar_plantilla'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', resp['Content-Disposition'])

    def test_limpiar_datos(self):
        self.client.force_login(self.auth_contador)
        archivo = self._generar_archivo_post([FILA_BALANCE_SANO])
        self.client.post(reverse('moduloETL:carga_datos'), {'tipo_documento': 'Balance General', 'archivo_datos': archivo})

        self.assertIsNotNone(EstadoCarga.actual().ruta_csv)
        resp = self.client.post(reverse('moduloETL:limpiar_datos'), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(EstadoCarga.actual().ruta_csv)

    def test_rf10_vista_ratios_modal_outliers(self):
        """[RF-10] Verifica que la vista de ratios detecte anomalías y renderice el modal de advertencia."""
        self.client.force_login(self.auth_contador)
        # Crear un ratio con anomalía (margen 150%)
        RatioFinanciero.objects.create(
            empresa=self.empresa1,
            periodo='2025-Q4',
            v1_razon_corriente=Decimal("1.80"),
            v5_margen_operacional=Decimal("1.50"),
        )
        resp = self.client.get(reverse('moduloETL:ratios_financieros'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['tiene_anomalias'])
        self.assertGreaterEqual(resp.context['total_anomalias'], 1)
        self.assertContains(resp, 'modalAdvertenciaOutliersETL')
        self.assertContains(resp, 'Valores Anómalos (Outliers) Detectados')
        self.assertContains(resp, 'Forzar Ejecución (Aceptar Alerta)')

    def test_rf11_boton_ejecutar_analisis_y_spinner_carga(self):
        """
        [RF-11] Como Contador, quiero iniciar manualmente la ejecución del modelo...
        Verifica que la interfaz de ratios contables contenga el botón 'Ejecutar Análisis'
        y el modal con spinner/barra de progreso de carga.
        """
        self.client.force_login(self.auth_contador)
        RatioFinanciero.objects.create(
            empresa=self.empresa1,
            periodo='2025-Q4',
            v1_razon_corriente=Decimal("1.80"),
            v2_capital_trabajo_activos=Decimal("0.25"),
            v3_leverage_total=Decimal("0.60"),
            v4_roa_operacional=Decimal("0.10"),
            v5_margen_operacional=Decimal("0.12"),
            v6_rotacion_activos=Decimal("1.20"),
        )

        resp = self.client.get(reverse('moduloETL:ratios_financieros'))
        self.assertEqual(resp.status_code, 200)

        # 1. Presencia del botón "Ejecutar Análisis"
        self.assertContains(resp, 'Ejecutar Análisis')

        # 2. Presencia del componente de spinner y barra de carga (RF-11)
        self.assertContains(resp, 'modalCargaAnalisis')
        self.assertContains(resp, 'spinner-border')
        self.assertContains(resp, 'barraProgresoAnalisis')
        self.assertContains(resp, 'progress-bar-animated')
        self.assertContains(resp, 'Ejecutando Modelo de Random Forest')

    def test_rf11_contador_inicia_ejecucion_modelo_random_forest(self):
        """
        [RF-11] Verifica que el Contador pueda iniciar manualmente el modelo
        de Random Forest, el proceso tarde menos de 10s y redirija automáticamente al
        dashboard con mensaje de éxito y resultados actualizados.
        """
        import time
        from capaAnalitica.models import PrediccionRiesgo

        self.client.force_login(self.auth_contador)

        ratio = RatioFinanciero.objects.create(
            empresa=self.empresa1,
            periodo='2025-Q4',
            v1_razon_corriente=Decimal("1.80"),
            v2_capital_trabajo_activos=Decimal("0.25"),
            v3_leverage_total=Decimal("0.60"),
            v4_roa_operacional=Decimal("0.10"),
            v5_margen_operacional=Decimal("0.12"),
            v6_rotacion_activos=Decimal("1.20"),
        )

        t_inicio = time.time()
        resp = self.client.post(reverse('moduloETL:ejecutar_analisis'), follow=False)
        duracion_segundos = time.time() - t_inicio

        # Criterio: El proceso no debe tardar más de 10 segundos
        self.assertLess(duracion_segundos, 10.0)

        # Criterio: Redirige automáticamente al dashboard del Dueño
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('dashboard:dashboard'))

        # Seguir redirección y verificar mensaje de éxito
        resp_dashboard = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(resp_dashboard.status_code, 200)

        # Verificar que se creó la predicción en base de datos
        prediccion = PrediccionRiesgo.objects.filter(empresa=self.empresa1, ratio=ratio).first()
        self.assertIsNotNone(prediccion)
        self.assertGreaterEqual(float(prediccion.score_riesgo), 0.0)
        self.assertIn(prediccion.nivel_semaforo, ['Verde', 'Amarillo', 'Rojo'])

    def test_rf11_ejecutar_analisis_periodo_especifico(self):
        """[RF-11] Verifica la ejecución manual especificando un 'ratio_id' de período."""
        from capaAnalitica.models import PrediccionRiesgo

        self.client.force_login(self.auth_contador)

        ratio_q1 = RatioFinanciero.objects.create(
            empresa=self.empresa1,
            periodo='2025-Q1',
            v1_razon_corriente=Decimal("1.50"),
            v2_capital_trabajo_activos=Decimal("0.20"),
            v3_leverage_total=Decimal("0.80"),
            v4_roa_operacional=Decimal("0.08"),
            v5_margen_operacional=Decimal("0.10"),
            v6_rotacion_activos=Decimal("1.10"),
        )

        resp = self.client.post(
            reverse('moduloETL:ejecutar_analisis'),
            {'ratio_id': str(ratio_q1.id)},
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        prediccion = PrediccionRiesgo.objects.filter(empresa=self.empresa1, ratio=ratio_q1).first()
        self.assertIsNotNone(prediccion)

    def test_rnf10_settings_limite_subida_25mb(self):
        """[RNF-10] Verifica configuración de settings para soportar hasta 25 MB sin caídas."""
        from django.conf import settings
        self.assertGreaterEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 25 * 1024 * 1024)
        self.assertGreaterEqual(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, 25 * 1024 * 1024)

    def test_rnf10_form_rechaza_archivo_mayor_a_25mb(self):
        """[RNF-10] Verifica que CargaArchivoForm rechace archivos mayores a 25 MB con mensaje amigable."""
        archivo_grande = SimpleUploadedFile('balance_pesado.csv', b'col1,col2\n1,2', content_type='text/csv')
        # Simular tamaño mayor a 25 MB (ej. 26 MB)
        archivo_grande.size = 26 * 1024 * 1024

        form = CargaArchivoForm(
            data={'tipo_documento': 'Balance General'},
            files={'archivo_datos': archivo_grande}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('archivo_datos', form.errors)
        error_msg = str(form.errors['archivo_datos'])
        self.assertIn('25 MB', error_msg)

    def test_rnf10_form_acepta_archivo_hasta_25mb(self):
        """[RNF-10] Verifica que CargaArchivoForm acepte archivos válidos dentro de los 25 MB."""
        archivo_valido = SimpleUploadedFile('balance_ok.csv', b'col1,col2\n1,2', content_type='text/csv')
        # Simular tamaño de 15 MB
        archivo_valido.size = 15 * 1024 * 1024

        form = CargaArchivoForm(
            data={'tipo_documento': 'Balance General'},
            files={'archivo_datos': archivo_valido}
        )
        self.assertTrue(form.is_valid())

    def test_rnf10_servicio_rechaza_archivo_mayor_a_25mb(self):
        """[RNF-10] Verifica que el servicio de extracción ETL rechace archivos > 25 MB sin saturar el backend."""
        archivo_grande = SimpleUploadedFile('balance_grande.csv', b'datos...', content_type='text/csv')
        archivo_grande.size = 26 * 1024 * 1024

        df_out, errs = extraer_dataframe_desde_archivo(archivo_grande)
        self.assertIsNone(df_out)
        self.assertTrue(any('25 MB' in e and 'RNF-10' in e for e in errs))

    def test_rnf10_frontend_elementos_y_script_en_carga_datos(self):
        """[RNF-10] Verifica que la plantilla carga_datos.html contenga la alerta y script de validación inmediata."""
        self.client.force_login(self.auth_contador)
        resp = self.client.get(reverse('moduloETL:carga_datos'))
        self.assertEqual(resp.status_code, 200)

        content = resp.content.decode('utf-8')
        # Contenedor de alerta frontend
        self.assertIn('alertaTamanoArchivo', content)
        self.assertIn('mensajeTamanoArchivo', content)
        # Constante y validación de 25 MB en el script
        self.assertIn('25 * 1024 * 1024', content)
        self.assertIn('RNF-10', content)
        self.assertIn('Archivo seleccionado correctamente', content)
