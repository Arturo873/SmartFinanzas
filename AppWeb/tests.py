import os

import pandas as pd
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import EstadoCarga, PerfilUsuario
from .variables_modelo import (
    CLAVES_MODELO,
    LEVERAGE_MAXIMO,
    MINIMO_CIERRES_VOLATILIDAD,
    calcular_variables_financieras,
    calcular_variables_modelo,
    calcular_volatilidad_flujo_caja,
    calcular_zem_altman,
)
from .views import COLUMNAS_PLANTILLA
from .viewsML import analizar_contribucion_riesgo, obtener_metricas_modelo_oficial, predecir_riesgo

FILA_SANA = {
    'Id_Empresa': 'EMP-1', 'Periodo': '2024-Q4',
    'Activo_Circulante': 500.0, 'Pasivo_Circulante': 250.0,
    'Efectivo_Equivalentes': 100.0, 'Inventarios': 150.0,
    'Activo_Total': 1000.0, 'Pasivo_Total': 400.0, 'Patrimonio_Neto': 600.0,
    'Utilidad_Neta': 60.0, 'Ingresos_Netos': 1200.0, 'EBIT': 90.0,
    'Utilidades_Retenidas': 200.0,
}


class VariablesModeloTests(TestCase):
    def test_formulas_del_miro(self):
        v = calcular_variables_financieras(FILA_SANA)
        self.assertAlmostEqual(v['razon_corriente'], 2.0)
        self.assertAlmostEqual(v['capital_trabajo_sobre_activos'], 0.25)
        self.assertAlmostEqual(v['leverage_total'], 400 / 600)
        self.assertAlmostEqual(v['roa_operacional'], 0.09)
        self.assertAlmostEqual(v['margen_operacional'], 0.075)
        self.assertAlmostEqual(v['rotacion_activos'], 1.2)

    def test_patrimonio_negativo_es_riesgo_maximo(self):
        fila = {**FILA_SANA, 'Pasivo_Total': 1100.0, 'Patrimonio_Neto': -100.0}
        self.assertEqual(calcular_variables_financieras(fila)['leverage_total'], LEVERAGE_MAXIMO)

    def test_sin_ingresos_y_ebit_negativo_es_el_peor_margen(self):
        fila = {**FILA_SANA, 'Ingresos_Netos': 0.0, 'EBIT': -50.0}
        self.assertEqual(calcular_variables_financieras(fila)['margen_operacional'], -1.0)

    def test_volatilidad_requiere_minimo_de_cierres(self):
        pocos = [10.0] * (MINIMO_CIERRES_VOLATILIDAD - 1)
        self.assertIsNone(calcular_volatilidad_flujo_caja(pocos, pocos))

        flujos = [10.0, -10.0] * (MINIMO_CIERRES_VOLATILIDAD // 2)
        ingresos = [100.0] * MINIMO_CIERRES_VOLATILIDAD
        self.assertGreater(calcular_volatilidad_flujo_caja(flujos, ingresos), 0)

    def test_zem_altman(self):
        # 3.25 + 6.56*0.25 + 3.26*0.2 + 6.72*0.09 + 1.05*1.5
        self.assertAlmostEqual(calcular_zem_altman(FILA_SANA), 7.7218, places=4)

    def test_variables_modelo_en_orden_y_completas(self):
        variables = calcular_variables_modelo(FILA_SANA)
        self.assertEqual(list(variables), CLAVES_MODELO)
        self.assertEqual(len(variables), 7)


# Pasivos mayores que activos y pérdida operacional: insolvente según Z''EM.
FILA_EN_CRISIS = {
    **FILA_SANA, 'Activo_Circulante': 200.0, 'Pasivo_Circulante': 700.0,
    'Pasivo_Total': 1100.0, 'Patrimonio_Neto': -100.0, 'EBIT': -150.0,
    'Utilidades_Retenidas': -400.0, 'Ingresos_Netos': 600.0,
}


class ModeloV10Tests(TestCase):
    def test_puntaje_en_rango_y_empresa_en_crisis_mas_riesgosa(self):
        sana = calcular_variables_modelo(FILA_SANA)
        crisis = calcular_variables_modelo(FILA_EN_CRISIS)
        puntaje_sana, _, _ = predecir_riesgo(sana)
        puntaje_crisis, _, color_crisis = predecir_riesgo(crisis)
        self.assertTrue(0 <= puntaje_sana <= 100 and 0 <= puntaje_crisis <= 100)
        self.assertGreater(puntaje_crisis, puntaje_sana)
        self.assertEqual(color_crisis, 'Rojo')

    def test_explicabilidad_muestra_hasta_3_variables_que_suben_el_riesgo(self):
        crisis = calcular_variables_modelo(FILA_EN_CRISIS)
        factores = analizar_contribucion_riesgo(crisis)
        self.assertTrue(1 <= len(factores) <= 3)
        self.assertTrue(all(f['impacto'] > 0 for f in factores))
        self.assertNotIn('volatilidad_flujo_caja', [f['key'] for f in factores])

    def test_metricas_cumplen_meta_minima_de_rnf08(self):
        # Meta propuesta para RNF-08 v11, medida en empresas reales no vistas.
        metricas = obtener_metricas_modelo_oficial()
        self.assertGreaterEqual(metricas['recall'], 70)
        self.assertGreaterEqual(metricas['f1_score'], 70)


class CargaYPrediccionTests(TestCase):
    def setUp(self):
        self.contador = User.objects.create_user('contador', password='x')
        PerfilUsuario.objects.create(user=self.contador, rol=PerfilUsuario.ROL_CONTADOR)
        self.dueno = User.objects.create_user('dueno', password='x')
        PerfilUsuario.objects.create(user=self.dueno, rol=PerfilUsuario.ROL_DUENO)

    def tearDown(self):
        ruta = EstadoCarga.actual().ruta_csv
        if ruta and os.path.exists(ruta):
            os.remove(ruta)

    def _subir(self, filas):
        csv = pd.DataFrame(filas).to_csv(index=False).encode('utf-8')
        self.client.force_login(self.contador)
        return self.client.post(reverse('carga_datos'), {
            'tipo_documento': 'balance',
            'archivo_datos': SimpleUploadedFile('carga.csv', csv, content_type='text/csv'),
        })

    def test_rechaza_plantilla_sin_columnas_v8(self):
        fila = {k: v for k, v in FILA_SANA.items() if k not in ('EBIT', 'Ingresos_Netos', 'Utilidades_Retenidas')}
        self._subir([fila])
        self.assertIsNone(EstadoCarga.actual().ruta_csv)

    def test_rechaza_activo_corriente_mayor_que_activo_total(self):
        self._subir([{**FILA_SANA, 'Activo_Circulante': 1500.0}])
        self.assertIsNone(EstadoCarga.actual().ruta_csv)

    def test_carga_y_prediccion_con_plantilla_v8(self):
        self._subir([FILA_SANA])
        self.assertIsNotNone(EstadoCarga.actual().ruta_csv)
        self.assertEqual(set(COLUMNAS_PLANTILLA), set(FILA_SANA))

        self.client.force_login(self.dueno)
        respuesta = self.client.post(reverse('prediccion'), {'empresa_id': 'EMP-1'})
        self.assertEqual(respuesta.status_code, 200)
        claves = [v['clave'] for v in respuesta.context['variables_modelo']]
        self.assertEqual(claves, CLAVES_MODELO)
        self.assertNotContains(respuesta, 'Banco Central')
        self.assertContains(respuesta, 'Variables del Modelo Predictivo')

    def test_prediccion_se_habilita_solo_con_la_carga(self):
        self._subir([FILA_SANA])
        respuesta = self.client.get(reverse('home'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, 'CAPM')

        self.client.force_login(self.dueno)
        respuesta = self.client.get(reverse('home'))
        self.assertContains(respuesta, 'EJECUTAR PREDICCIÓN')
        self.assertNotContains(respuesta, 'CAPM')
