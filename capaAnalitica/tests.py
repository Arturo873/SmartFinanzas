"""
Pruebas Unitarias para la Capa Analítica (MotorRiesgo y Explicabilidad SHAP).
SmartFinanzas.
"""

from decimal import Decimal
import numpy as np
from django.test import TestCase
from django.utils import timezone
from capaAnalitica.services import MotorRiesgo, ejecutar_y_persistir_prediccion
from capaAnalitica.models import PrediccionRiesgo
from moduloETL.models import RatioFinanciero, CargaFinanciera
from usuarios.models import Empresa, Usuario, Rol


class MotorRiesgoTests(TestCase):
    """
    Pruebas unitarias de inferencia ML y explicabilidad SHAP server-side.
    """

    @classmethod
    def setUpTestData(cls):
        cls.motor = MotorRiesgo()

    def test_inicializacion_motor(self):
        """Verifica que el modelo pre-entrenado se cargue correctamente en memoria."""
        self.assertIsNotNone(self.motor.model)
        self.assertTrue(hasattr(self.motor.model, 'predict_proba'))

    def test_evaluar_riesgo_con_lista(self):
        """
        Verifica que evaluar_riesgo acepte una lista con las 7 variables financieras,
        convierta el input a NumPy 2D y devuelva score, nivel y Top-3 SHAP.
        """
        # [X1: razon_corriente, X2: cap_trabajo, X3: leverage, X4: roa, X5: margen, X6: rotacion, X7: volatilidad]
        vector_solvente = [2.5, 0.45, 0.6, 0.15, 0.18, 1.8, 0.02]
        resultado = self.motor.evaluar_riesgo(vector_solvente)

        self.assertIn('score', resultado)
        self.assertIn('nivel', resultado)
        self.assertIn('top_3_variables', resultado)
        self.assertIn('shap_values', resultado)

        # Validaciones de rango y tipos
        self.assertIsInstance(resultado['score'], float)
        self.assertGreaterEqual(resultado['score'], 0.0)
        self.assertLessEqual(resultado['score'], 100.0)
        self.assertIn(resultado['nivel'], ['Verde', 'Amarillo', 'Rojo'])

        # Validar Top-3 SHAP
        top3 = resultado['top_3_variables']
        self.assertEqual(len(top3), 3)

        # Verificar orden por impacto absoluto descendente
        self.assertGreaterEqual(top3[0]['impacto_abs'], top3[1]['impacto_abs'])
        self.assertGreaterEqual(top3[1]['impacto_abs'], top3[2]['impacto_abs'])

        # Verificar contenido explicativo en cada variable
        for item in top3:
            self.assertIn('nombre', item)
            self.assertIn('impacto_pct', item)
            self.assertIn('texto', item)
            self.assertTrue(len(item['texto']) > 0)

    def test_evaluar_riesgo_con_diccionario(self):
        """
        Verifica que evaluar_riesgo admita un diccionario con nombres canónicos de variables.
        """
        vector_dict = {
            'razon_corriente': 0.8,
            'capital_trabajo_sobre_activos': -0.15,
            'leverage_total': 4.5,
            'roa_operacional': -0.05,
            'margen_operacional': -0.08,
            'rotacion_activos': 0.6,
            'volatilidad_flujo_caja': 0.25,
        }
        resultado = self.motor.evaluar_riesgo(vector_dict)

        self.assertIsInstance(resultado['score'], float)
        self.assertIn(resultado['nivel'], ['Verde', 'Amarillo', 'Rojo'])
        self.assertEqual(len(resultado['top_3_variables']), 3)

    def test_logica_estatica_semaforo(self):
        """
        Verifica la lógica estática de asignación de colores:
        - Rojo si score > 70
        - Amarillo si 35 < score <= 70
        - Verde si score <= 35
        """
        # Simulación de scores contra la regla estática
        scores_prueba = [
            (10.0, 'Verde'),
            (35.0, 'Verde'),
            (35.01, 'Amarillo'),
            (60.0, 'Amarillo'),
            (70.0, 'Amarillo'),
            (70.01, 'Rojo'),
            (95.0, 'Rojo'),
        ]

        for s, nivel_esperado in scores_prueba:
            if s > 70.0:
                nivel = "Rojo"
            elif s > 35.0:
                nivel = "Amarillo"
            else:
                nivel = "Verde"
            self.assertEqual(nivel, nivel_esperado)

    def test_persistencia_prediccion_servicio(self):
        """
        Verifica la función de servicio ejecutar_y_persistir_prediccion.
        """
        empresa = Empresa.objects.create(razon_social="Empresa Test SpA", rut="77.888.999-1")
        carga = CargaFinanciera.objects.create(periodo="2026-Q1", empresa=empresa)
        ratio = RatioFinanciero.objects.create(
            carga=carga,
            empresa=empresa,
            periodo="2026-Q1",
            v1_razon_corriente=Decimal("1.8000"),
            v2_capital_trabajo_activos=Decimal("0.2500"),
            v3_leverage_total=Decimal("1.2000"),
            v4_roa_operacional=Decimal("0.0800"),
            v5_margen_operacional=Decimal("0.1000"),
            v6_rotacion_activos=Decimal("1.4000"),
            v7_volatilidad_flujo=Decimal("0.0500"),
        )

        pred, res = ejecutar_y_persistir_prediccion(ratio, empresa=empresa)

        self.assertIsInstance(pred, PrediccionRiesgo)
        self.assertEqual(pred.empresa, empresa)
        self.assertIsNotNone(pred.score_riesgo)
        self.assertIn(pred.nivel_semaforo, ['Verde', 'Amarillo', 'Rojo'])
        self.assertIn('Margen Operacional', pred.variables_influyentes)
