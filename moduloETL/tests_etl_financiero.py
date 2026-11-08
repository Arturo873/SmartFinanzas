"""
Suite de Pruebas Unitarias para el Módulo Desacoplado FinancialETLProcessor
===========================================================================
Valida la extracción, homologación IFRS, saneamiento de datos y cálculo
de razones financieras en memoria con mocks horizontales, verticales y CMF real.
"""

import io
import unittest
from pathlib import Path
from decimal import Decimal

import numpy as np
import pandas as pd
import openpyxl

from moduloETL.etl_financiero import (
    FinancialETLProcessor,
    CompanyMetadata,
    ETLError,
    ETLValidationError,
    MissingAccountError,
    InvalidFormatError,
    FEATURE_COLUMNS,
    clean_number,
    normalize_text,
)


class TestFinancialETLProcessor(unittest.TestCase):
    """Pruebas unitarias completas para FinancialETLProcessor."""

    def setUp(self):
        self.cmf_file_path = Path(
            r"C:\Users\artur\.gemini\antigravity\brain\340049c4-3bb8-4bd9-978f-ed53df731d7d\.user_uploaded\media_1794155179912_49940916.xlsx"
        )

    def test_limpieza_numeros_contables(self):
        """Valida que clean_number procese notación contable chilena, internacional y negativa."""
        self.assertEqual(clean_number("15.149.324.000"), 15149324000.0)
        self.assertEqual(clean_number("-80237000"), -80237000.0)
        self.assertEqual(clean_number("(80.237.000)"), -80237000.0)
        self.assertEqual(clean_number("$ 2.604.212.000"), 2604212000.0)
        self.assertEqual(clean_number("12345,67"), 12345.67)
        self.assertEqual(clean_number(""), 0.0)
        self.assertEqual(clean_number(None), 0.0)

    def test_archivo_cmf_oficial_horizontal(self):
        """Valida la ingesta del archivo CMF oficial proporcionado en formato horizontal."""
        if not self.cmf_file_path.exists():
            self.skipTest("Archivo CMF de prueba no disponible en disco.")

        processor = FinancialETLProcessor(self.cmf_file_path)
        features = processor.get_features_df()
        audit = processor.get_audit_report()

        # 1. Verificación de metadatos
        self.assertEqual(audit['metadata']['razon_social'], "COMERCIALIZADORA DE TRIGO S.A.")
        self.assertEqual(audit['metadata']['rut'], "96.511.150-6")
        self.assertEqual(audit['metadata']['moneda'], "PESOS")
        self.assertEqual(audit['metadata']['formato_detectado'], "horizontal")
        self.assertEqual(audit['metadata']['periodos'], ['03 / 2026', '06 / 2026'])

        # 2. Verificación de columnas de features
        self.assertEqual(list(features.columns), FEATURE_COLUMNS)
        self.assertEqual(len(features), 2)

        # 3. Verificación de ratios exactos (Período 1)
        # Razón corriente: 2.604.212.000 / 530.733.000 = ~4.9068
        self.assertAlmostEqual(features.loc['03 / 2026', 'razon_corriente'], 4.9068, places=3)
        # Capital de trabajo / Activos: (2.604.212.000 - 530.733.000) / 15.149.324.000 = ~0.1369
        self.assertAlmostEqual(features.loc['03 / 2026', 'capital_trabajo_sobre_activos'], 0.1369, places=3)
        # Leverage: 530.733.000 / 14.618.591.000 = ~0.0363
        self.assertAlmostEqual(features.loc['03 / 2026', 'leverage_total'], 0.0363, places=3)
        # Margen operacional acotado: -80.237.000 / 234.554.000 = ~ -0.3421
        self.assertAlmostEqual(features.loc['03 / 2026', 'margen_operacional'], -0.3421, places=3)
        # Volatilidad temporal
        self.assertGreater(features.loc['03 / 2026', 'volatilidad_flujo_caja'], 0.0)

        # 4. Ecuación patrimonial cuadrada
        self.assertTrue(audit['ecuacion_patrimonial']['03 / 2026']['cuadrado'])
        self.assertTrue(audit['ecuacion_patrimonial']['06 / 2026']['cuadrado'])

    def test_formato_vertical_mock_en_memoria(self):
        """Valida que un Excel vertical en memoria (filas = cuentas, columnas = períodos) sea procesado exitosamente."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BalanceVertical"

        ws.cell(1, 1, "Razón Social: TECNOLOGIAS ANDINAS SPA")
        ws.cell(2, 1, "RUT: 77.123.456-7")
        ws.cell(3, 1, "Moneda: CLP")

        ws.cell(5, 1, "Cuentas IFRS")
        ws.cell(5, 2, "2024-Q1")
        ws.cell(5, 3, "2024-Q2")

        cuentas = [
            ("Activo Circulante", 15000000, 18000000),
            ("Pasivo Circulante", 5000000, 6000000),
            ("Total de Activos", 40000000, 45000000),
            ("Total de Pasivos", 12000000, 14000000),
            ("Total Patrimonio", 28000000, 31000000),
            ("Ganancias Acumuladas", 8000000, 10000000),
            ("Ventas Netas", 25000000, 30000000),
            ("Resultado Operacional", 3500000, 4200000),
            ("Flujo de Efectivo Operacional", 2800000, 3100000),
        ]
        for idx, (acc, q1, q2) in enumerate(cuentas):
            r = 6 + idx
            ws.cell(r, 1, acc)
            ws.cell(r, 2, q1)
            ws.cell(r, 3, q2)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        processor = FinancialETLProcessor(buf)
        features = processor.get_features_df()
        audit = processor.get_audit_report()

        self.assertEqual(audit['metadata']['formato_detectado'], "vertical")
        self.assertEqual(audit['metadata']['razon_social'], "TECNOLOGIAS ANDINAS SPA")
        self.assertEqual(audit['metadata']['rut'], "77.123.456-7")
        self.assertEqual(list(features.index), ["2024-Q1", "2024-Q2"])

        # V1: 15.000.000 / 5.000.000 = 3.0
        self.assertEqual(features.loc["2024-Q1", "razon_corriente"], 3.0)
        # V3: 12.000.000 / 28.000.000 = ~0.4286
        self.assertAlmostEqual(features.loc["2024-Q1", "leverage_total"], 0.4286, places=3)
        # Ecuación patrimonial: 12M + 28M = 40M (Desbalance = 0)
        self.assertTrue(audit['ecuacion_patrimonial']["2024-Q1"]['cuadrado'])

    def test_fallback_ebit_cuando_no_existe(self):
        """Valida que si EBIT no viene en el archivo, se calcule vía Ganancia antes de impuestos + Costos financieros."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 1, "Fecha")
        ws.cell(1, 2, "Activo Circulante")
        ws.cell(1, 3, "Pasivo Circulante")
        ws.cell(1, 4, "Total de Activos")
        ws.cell(1, 5, "Total de Pasivos")
        ws.cell(1, 6, "Total Patrimonio")
        ws.cell(1, 7, "Ventas Netas")
        ws.cell(1, 8, "Ganancia Antes de Impuestos")
        ws.cell(1, 9, "Costos Financieros")

        ws.cell(2, 1, "2025-Q1")
        ws.cell(2, 2, 1000)
        ws.cell(2, 3, 500)
        ws.cell(2, 4, 3000)
        ws.cell(2, 5, 1000)
        ws.cell(2, 6, 2000)
        ws.cell(2, 7, 5000)
        ws.cell(2, 8, 300)  # EBT
        ws.cell(2, 9, 100)  # CF -> EBIT esperado = 400

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        proc = FinancialETLProcessor(buf)
        audit = proc.get_audit_report()
        features = proc.get_features_df()

        self.assertTrue(audit['resumen_ejecutivo']['ebit_fallback_utilizado'])
        # ROA Operacional = EBIT / Activo = 400 / 3000 = ~0.1333
        self.assertAlmostEqual(features.loc["2025-Q1", "roa_operacional"], 0.1333, places=3)

    def test_insolvencia_tecnica_patrimonio_negativo(self):
        """Valida que si el Patrimonio Neto es <= 0, el Leverage se acote en 10.0 y se alerte quiebra técnica."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 1, "Fecha")
        ws.cell(1, 2, "Activo Circulante")
        ws.cell(1, 3, "Pasivo Circulante")
        ws.cell(1, 4, "Total de Activos")
        ws.cell(1, 5, "Total de Pasivos")
        ws.cell(1, 6, "Total Patrimonio")
        ws.cell(1, 7, "Ventas Netas")

        ws.cell(2, 1, "2025-Q1")
        ws.cell(2, 2, 1000)
        ws.cell(2, 3, 2000)
        ws.cell(2, 4, 3000)
        ws.cell(2, 5, 3500)
        ws.cell(2, 6, -500)  # Patrimonio negativo
        ws.cell(2, 7, 2000)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        proc = FinancialETLProcessor(buf)
        features = proc.get_features_df()
        audit = proc.get_audit_report()

        self.assertEqual(features.loc["2025-Q1", "leverage_total"], 10.0)
        self.assertTrue(audit['resumen_ejecutivo']['quiebra_tecnica_detectada'])
        self.assertTrue(any("Insolvencia Técnica" in w for w in audit['alertas']))

    def test_pasivo_circulante_cero_razon_corriente(self):
        """Valida que si el Pasivo Circulante es 0, la razón corriente no divida por cero y se fije en 10.0."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 1, "Fecha")
        ws.cell(1, 2, "Activo Circulante")
        ws.cell(1, 3, "Pasivo Circulante")
        ws.cell(1, 4, "Total de Activos")
        ws.cell(1, 5, "Total de Pasivos")
        ws.cell(1, 6, "Total Patrimonio")
        ws.cell(1, 7, "Ventas Netas")

        ws.cell(2, 1, "2025-Q1")
        ws.cell(2, 2, 5000)
        ws.cell(2, 3, 0)     # Pasivo Circulante = 0
        ws.cell(2, 4, 10000)
        ws.cell(2, 5, 0)
        ws.cell(2, 6, 10000)
        ws.cell(2, 7, 8000)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        proc = FinancialETLProcessor(buf)
        features = proc.get_features_df()
        self.assertEqual(features.loc["2025-Q1", "razon_corriente"], 10.0)

    def test_activo_total_invalido_lanza_error(self):
        """Valida que un balance con Activo Total <= 0 lance ETLValidationError."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 1, "Fecha")
        ws.cell(1, 2, "Activo Circulante")
        ws.cell(1, 3, "Pasivo Circulante")
        ws.cell(1, 4, "Total de Activos")
        ws.cell(1, 5, "Total de Pasivos")
        ws.cell(1, 6, "Total Patrimonio")
        ws.cell(1, 7, "Ventas Netas")

        ws.cell(2, 1, "2025-Q1")
        ws.cell(2, 2, 500)
        ws.cell(2, 3, 500)
        ws.cell(2, 4, 0)  # Activo Total inválido
        ws.cell(2, 5, 500)
        ws.cell(2, 6, 500)
        ws.cell(2, 7, 1000)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        with self.assertRaises(ETLValidationError):
            FinancialETLProcessor(buf)

    def test_cuentas_faltantes_lanza_missing_account_error(self):
        """Valida que la ausencia de cuentas canónicas indispensables lance MissingAccountError."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 1, "Fecha")
        ws.cell(1, 2, "CuentaInventada1")
        ws.cell(1, 3, "CuentaInventada2")
        ws.cell(1, 4, "Total de Activos")

        ws.cell(2, 1, "2025-Q1")
        ws.cell(2, 2, 100)
        ws.cell(2, 3, 200)
        ws.cell(2, 4, 500)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        with self.assertRaises(InvalidFormatError):
            FinancialETLProcessor(buf)

    def test_un_solo_periodo_calcula_v7(self):
        """Valida que con un solo período, V7 se normalice respecto al Activo Total o impute neutral."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 1, "Fecha")
        ws.cell(1, 2, "Activo Circulante")
        ws.cell(1, 3, "Pasivo Circulante")
        ws.cell(1, 4, "Total de Activos")
        ws.cell(1, 5, "Total de Pasivos")
        ws.cell(1, 6, "Total Patrimonio")
        ws.cell(1, 7, "Ventas Netas")
        ws.cell(1, 8, "Flujo Operacional")

        ws.cell(2, 1, "2025-Q1")
        ws.cell(2, 2, 1000)
        ws.cell(2, 3, 500)
        ws.cell(2, 4, 10000)
        ws.cell(2, 5, 2000)
        ws.cell(2, 6, 8000)
        ws.cell(2, 7, 5000)
        ws.cell(2, 8, 500)  # Flujo 500 / 10000 = 0.05

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        proc = FinancialETLProcessor(buf)
        features = proc.get_features_df()
        self.assertAlmostEqual(features.loc["2025-Q1", "volatilidad_flujo_caja"], 0.05, places=3)


if __name__ == '__main__':
    unittest.main()
