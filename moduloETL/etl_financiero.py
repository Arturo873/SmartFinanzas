"""
Módulo ETL Financiero Desacoplado Orientado a Objetos (SmartFinanzas)
====================================================================
Módulo de arquitectura limpia especializado en FinTech y Machine Learning.
Encargado de procesar archivos contables (.xlsx, .xls, .csv) de empresas bajo
normativa IFRS / CMF para extraer estados financieros y generar vectores
adimensionales limpios de 7 razones financieras para inferencia predictiva.

Características Arquitectónicas:
--------------------------------
1. Cero dependencias de Base de Datos: procesa puramente en memoria con pandas y openpyxl.
2. Soporte polimórfico de entrada: acepta rutas en disco (str/Path), buffers (BytesIO/BinaryIO),
   archivos cargados web (Django UploadedFile) o pd.DataFrame directo.
3. Detección automática de orientación contable:
   - Formato Horizontal (CMF oficial): columnas = cuentas contables, filas = períodos.
   - Formato Vertical (PYME tradicional): filas = cuentas contables, columnas = períodos.
4. Homologación IFRS CMF: mapeo exhaustivo de sinónimos contables y fallback para EBIT.
5. Validación y saneamiento contable: verificación de Activo Total > 0 y ecuación patrimonial.
6. Contención numérica estricta: acotamiento de ratios ML (V1 a V7) para prevenir overflow.
7. Doble entrega: DataFrame de features para inferencia y Reporte de Auditoría estructurado.
"""

import io
import re
import logging
import unicodedata
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Union, Any, BinaryIO

import numpy as np
import pandas as pd
import openpyxl

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. JERARQUÍA DE EXCEPCIONES GRANULARES
# ==============================================================================

class ETLError(Exception):
    """Excepción raíz para todas las anomalías y fallos del motor ETL Financiero."""
    pass


class ETLValidationError(ETLError):
    """Lanzada cuando los datos financieros violan axiomas contables indispensables (ej: Activo Total <= 0)."""
    pass


class MissingAccountError(ETLError):
    """Lanzada cuando una o más cuentas canónicas obligatorias no pudieron ser localizadas."""
    pass


class InvalidFormatError(ETLError):
    """Lanzada cuando el archivo contable no tiene una estructura legible o reconocible."""
    pass


# ==============================================================================
# 2. METADATOS Y ESTRUCTURAS DE DATOS
# ==============================================================================

@dataclass
class CompanyMetadata:
    """Metadatos de auditoría identificatorios de la empresa y del archivo contable."""
    razon_social: Optional[str] = None
    rut: Optional[str] = None
    moneda: Optional[str] = None
    periodos: List[str] = field(default_factory=list)
    formato_detectado: str = "horizontal"
    hoja_procesada: str = ""


# ==============================================================================
# 3. DICCIONARIO DE HOMOLOGACIÓN IFRS / CMF
# ==============================================================================

CANONICAL_SYNONYMS: Dict[str, List[str]] = {
    'Activo_Circulante': [
        'activoscorrientestotales',
        'totalactivoscorrientes',
        'totaldeactivoscorrientes',
        'activocirculante',
        'totalactivocirculante',
        'activoscorrientes',
        'activocorriente',
        'totaldeactivoscorrientesdistintosdelosactivoogruposdeactivosparasudisposicionclasificadoscomomantenidosparalaventaocomomantenidosparadistribuiralospropietarios',
    ],
    'Pasivo_Circulante': [
        'pasivoscorrientestotales',
        'totalpasivoscorrientes',
        'totaldepasivoscorrientes',
        'pasivocirculante',
        'totalpasivocirculante',
        'pasivoscorrientes',
        'pasivocorriente',
        'totaldepasivoscorrientesdistintosdelospasivosincluidosengruposdeactivosparasudisposicionclasificadoscomomantenidosparalaventa',
    ],
    'Activo_Total': [
        'totaldeactivos',
        'totalactivos',
        'activototal',
        'activostotales',
    ],
    'Pasivo_Total': [
        'totaldepasivos',
        'totalpasivos',
        'pasivototal',
        'pasivostotales',
    ],
    'Patrimonio_Neto': [
        'patrimoniototal',
        'patrimonioneto',
        'totalpatrimonio',
        'totalpatrimonioneto',
        'patrimonio',
        'patrimonioatribuiblealospropietariosdelacontroladora',
    ],
    'Utilidades_Retenidas': [
        'gananciasperdidasacumuladas',
        'utilidadesacumuladas',
        'utilidadesretenidas',
        'gananciasacumuladas',
        'resultadosacumulados',
        'utilidadacumulada',
    ],
    'Ingresos_Netos': [
        'ingresosdeactividadesordinarias',
        'ingresosordinarios',
        'ventasnetas',
        'ingresosnetos',
        'ingresosoperacionales',
        'ingresosdeexplotacion',
        'ingresostotales',
        'ventas',
    ],
    'EBIT': [
        'gananciasperdidasdeactividadesoperacionales',
        'resultadooperacional',
        'ebit',
        'utilidadoperacional',
        'resultadodeexplotacion',
        'gananciaoperacional',
    ],
    'Ganancia_Antes_Impuestos': [
        'gananciaperdidaantesdeimpuestos',
        'gananciaantesdeimpuestos',
        'resultadoantesdeimpuestoalarenta',
        'resultadoantesdeimpuestos',
        'utilidadantesdeimpuestos',
        'ebt',
    ],
    'Costos_Financieros': [
        'costosfinancieros',
        'gastosfinancieros',
        'gastosporinteresesyreajustes',
    ],
    'Flujo_Operacional': [
        'flujosdeefectivonetosprocedentesdeutilizadosenactividadesdeoperacion',
        'flujosdeefectivoprocedentesdeutilizadosenactividadesdeoperacion',
        'flujosdeefectivonetosprocedentesdeactividadesdeoperacion',
        'flujodeefectivonetosprocedentesdeutilizadosenactividadesdeoperacion',
        'flujodeefectivooperacional',
        'flujonetoactividadesoperacion',
        'flujooperacional',
    ]
}

FEATURE_COLUMNS: List[str] = [
    'razon_corriente',
    'capital_trabajo_sobre_activos',
    'leverage_total',
    'roa_operacional',
    'margen_operacional',
    'rotacion_activos',
    'volatilidad_flujo_caja',
]


# ==============================================================================
# 4. FUNCIONES DE NORMALIZACIÓN Y PARSEO NUMÉRICO
# ==============================================================================

def normalize_text(text: Any) -> str:
    """
    Normaliza texto contable a formato canónico sin acentos, minúsculas y sin puntuación.
    Ej: 'Ganancias (pérdidas) acumuladas' -> 'gananciasperdidasacumuladas'
    """
    if text is None:
        return ""
    s = str(text).strip().lower()
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]', '', s)


def clean_number(val: Any) -> float:
    """
    Parsea de manera defensiva cualquier representación numérica contable (monedas, miles, negativos).
    Ejemplos:
      '$ 15.149.324.000' -> 15149324000.0
      '(80.237.000)'     -> -80237000.0
      '-80237000'        -> -80237000.0
      '15149324,50'      -> 15149324.50
    """
    if val is None or val == "" or pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return 0.0

    # Conversión contable de paréntesis a signo negativo
    if s.startswith('(') and s.endswith(')'):
        s = '-' + s[1:-1].strip()

    # Remoción de signos monetarios y espacios
    s = re.sub(r'[$€£\s]', '', s)

    # Detección de separadores de miles y decimales
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif '.' in s and s.count('.') > 1:
        s = s.replace('.', '')
    elif ',' in s:
        s = s.replace(',', '.')

    try:
        return float(s)
    except ValueError:
        return 0.0


def match_canonical(norm_name: str) -> Optional[str]:
    """Retorna la cuenta canónica correspondiente a partir de un nombre normalizado."""
    if not norm_name:
        return None
    for canonical, syns in CANONICAL_SYNONYMS.items():
        for syn in syns:
            if norm_name == syn:
                return canonical
    return None


# ==============================================================================
# 5. MOTOR PRINCIPAL: FinancialETLProcessor
# ==============================================================================

class FinancialETLProcessor:
    """
    Procesador ETL desacoplado orientado a objetos para análisis de estados financieros e inferencia ML.
    """

    def __init__(
        self,
        source: Union[str, Path, BinaryIO, bytes, pd.DataFrame],
        sheet_name: Optional[Union[str, int]] = 0,
        neutral_v7: float = 0.0,
        force_layout: Optional[str] = None,
        auto_process: bool = True
    ) -> None:
        """
        Inicializa el procesador ETL.

        Args:
            source: Archivo en disco (str/Path), buffer binario (BytesIO), objeto archivo (UploadedFile),
                    o DataFrame directo.
            sheet_name: Nombre o índice de la hoja de Excel a procesar (por defecto la primera).
            neutral_v7: Valor neutral para V7 (volatilidad) en caso de balances con un único período puntual.
            force_layout: Forzar orientación 'horizontal' o 'vertical' (o None para auto-detección).
            auto_process: Si es True, ejecuta inmediatamente el pipeline de extracción y cálculo.
        """
        self.source = source
        self.sheet_name = sheet_name
        self.neutral_v7 = float(neutral_v7)
        self.force_layout = force_layout.lower() if force_layout else None
        self.auto_process = auto_process

        # Estado interno en memoria
        self._metadata = CompanyMetadata()
        self._accounts_df: pd.DataFrame = pd.DataFrame()
        self._features_df: pd.DataFrame = pd.DataFrame()
        self._warnings: List[str] = []
        self._ecuacion_patrimonial: Dict[str, Dict[str, Any]] = {}
        self._ebit_fallback_used: bool = False

        if self.auto_process:
            self.process()

    def process(self) -> "FinancialETLProcessor":
        """
        Ejecuta el ciclo de vida completo del pipeline ETL:
        Extract -> Detect Orientation -> Homologate -> Sanitize & Validate -> Compute Features.
        """
        # 1. Extracción de cuadrícula de celdas
        grid, sheet_title = self._load_grid()
        self._metadata.hoja_procesada = sheet_title

        # 2. Extracción de metadatos de encabezado
        self._extract_metadata(grid)

        # 3. Detección de orientación y extracción de cuentas canónicas
        self._accounts_df = self._extract_accounts(grid)

        # 4. Saneamiento, fallback de EBIT y validación contable
        self._validate_and_sanitize()

        # 5. Cálculo estricto de los 7 ratios financieros ML
        self._features_df = self._compute_ml_features()

        return self

    # --------------------------------------------------------------------------
    # FASE 1: EXTRACCIÓN (Extract)
    # --------------------------------------------------------------------------

    def _load_grid(self) -> Tuple[List[List[Any]], str]:
        """Carga la fuente en una matriz 2D de celdas en memoria de forma agnóstica al formato."""
        if isinstance(self.source, pd.DataFrame):
            df = self.source.copy()
            grid = [list(df.columns)] + df.values.tolist()
            return grid, "DataFrame"

        file_obj = self.source
        if isinstance(self.source, (str, Path)):
            path_str = str(self.source)
            if path_str.lower().endswith('.csv'):
                df = pd.read_csv(path_str, header=None, dtype=str)
                return df.fillna('').values.tolist(), "CSV"
            file_obj = open(path_str, 'rb')

        if isinstance(file_obj, (bytes, bytearray)):
            file_obj = io.BytesIO(file_obj)

        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

        # Intentar cargar como Excel vía openpyxl
        try:
            wb = openpyxl.load_workbook(file_obj, data_only=True)
            if isinstance(self.sheet_name, int):
                ws = wb.worksheets[self.sheet_name]
            elif isinstance(self.sheet_name, str) and self.sheet_name in wb.sheetnames:
                ws = wb[self.sheet_name]
            else:
                ws = wb.active

            grid = []
            for row in ws.iter_rows(values_only=True):
                grid.append(list(row))
            return grid, ws.title
        except Exception:
            # Fallback a lectura CSV delimitado (soporte de comas y punto y coma)
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            try:
                sample = file_obj.read(2048)
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                if isinstance(sample, bytes):
                    sample = sample.decode('utf-8', errors='ignore')
                first_line = sample.split('\n')[0] if sample else ''
                sep = ';' if ';' in first_line else ','
                df = pd.read_csv(file_obj, sep=sep, header=None, dtype=str)
                return df.fillna('').values.tolist(), "CSV_Fallback"
            except Exception as exc:
                raise InvalidFormatError(f"No fue posible leer el archivo como Excel (.xlsx/.xls) ni como CSV: {exc}")

    def _extract_metadata(self, grid: List[List[Any]]) -> None:
        """Extrae de los primeros renglones metadatos de la empresa: Razón Social, RUT, Moneda y Período."""
        max_scan = min(30, len(grid))
        for r in range(max_scan):
            row = grid[r]
            for val in row:
                if not val or not isinstance(val, str):
                    continue
                v_clean = val.strip()

                # Razón Social
                if not self._metadata.razon_social:
                    m_razon = re.search(r'(?:raz[oó]n\s*social|empresa|sociedad)\s*[:\s]\s*([^\n\r,;]+)', v_clean, re.I)
                    if m_razon:
                        self._metadata.razon_social = m_razon.group(1).strip()

                # RUT
                if not self._metadata.rut:
                    m_rut = re.search(r'(?:rut|identificaci[oó]n|tax\s*id)\s*[:\s]\s*([0-9kK\.\-]+)', v_clean, re.I)
                    if m_rut:
                        self._metadata.rut = m_rut.group(1).strip()
                    else:
                        m_rut_std = re.search(r'\b(\d{1,2}\.?\d{3}\.?\d{3}\-[\dkK])\b', v_clean)
                        if m_rut_std:
                            self._metadata.rut = m_rut_std.group(1).strip()

                # Moneda
                if not self._metadata.moneda:
                    m_moneda = re.search(r'(?:moneda|currency)\s*[:\s]\s*([a-zA-ZáéíóúÁÉÍÓÚ\s]+)', v_clean, re.I)
                    if m_moneda:
                        self._metadata.moneda = m_moneda.group(1).strip().upper()

                # Período
                m_periodo = re.search(r'(?:periodo|per[ií]odo)\s*[:\s]\s*([^\n\r,;]+)', v_clean, re.I)
                if m_periodo and not self._metadata.periodos:
                    self._metadata.periodos = [m_periodo.group(1).strip()]

    def _extract_accounts(self, grid: List[List[Any]]) -> pd.DataFrame:
        """
        Detecta la orientación de los estados financieros (Horizontal vs Vertical)
        y extrae las cuentas canónicas en un DataFrame unificado indexado por Período.
        """
        if not grid:
            raise InvalidFormatError("El archivo contable se encuentra vacío.")

        # 1. Escanear filas para detectar orientación horizontal (columnas = cuentas)
        best_row_idx = -1
        max_row_matches = 0
        row_canon_map: Dict[str, int] = {}

        for r_idx, row in enumerate(grid[:40]):
            matches: Dict[str, int] = {}
            for c_idx, cell in enumerate(row):
                norm = normalize_text(cell)
                canonical = match_canonical(norm)
                if canonical and canonical not in matches:
                    matches[canonical] = c_idx
            if len(matches) > max_row_matches:
                max_row_matches = len(matches)
                best_row_idx = r_idx
                row_canon_map = matches

        # 2. Escanear columnas para detectar orientación vertical (filas = cuentas)
        best_col_idx = -1
        max_col_matches = 0
        col_canon_map: Dict[str, int] = {}
        num_cols = max(len(r) for r in grid) if grid else 0

        for c_idx in range(min(15, num_cols)):
            matches = {}
            for r_idx, row in enumerate(grid):
                cell = row[c_idx] if c_idx < len(row) else None
                norm = normalize_text(cell)
                canonical = match_canonical(norm)
                if canonical and canonical not in matches:
                    matches[canonical] = r_idx
            if len(matches) > max_col_matches:
                max_col_matches = len(matches)
                best_col_idx = c_idx
                col_canon_map = matches

        # 3. Decidir orientación: El sistema procesa exclusivamente formato horizontal (CMF / IFRS)
        if self.force_layout == "horizontal" or self.force_layout is None:
            if max_row_matches >= 2:
                self._metadata.formato_detectado = "horizontal"
                return self._extract_horizontal(grid, best_row_idx, row_canon_map)
            elif max_col_matches >= 3:
                raise InvalidFormatError(
                    "El archivo parece estar estructurado en formato vertical. "
                    "El sistema opera exclusivamente con estados financieros en formato horizontal estandarizado CMF / IFRS "
                    "(donde las cuentas contables se ubican como encabezados de columnas y las filas representan períodos trimestrales). "
                    "Por favor transponga las cuentas a columnas antes de cargarlo."
                )
            else:
                raise InvalidFormatError(
                    f"No se detectaron suficientes cuentas contables canónicas reconocibles en formato horizontal. "
                    f"Coincidencias encontradas: {max_row_matches} (mínimo requerido: 2)."
                )
        elif self.force_layout == "vertical":
            raise InvalidFormatError(
                "La ingesta de estados en formato vertical está inhabilitada. "
                "El sistema opera exclusivamente con estados financieros horizontales bajo norma CMF / IFRS."
            )

    def _extract_horizontal(self, grid: List[List[Any]], header_row_idx: int, canon_map: Dict[str, int]) -> pd.DataFrame:
        """Extrae estados financieros en formato horizontal (ej. CMF oficial)."""
        header_row = grid[header_row_idx]

        col_fecha = None
        col_moneda = None
        for c_idx, cell in enumerate(header_row):
            norm = normalize_text(cell)
            if norm in ['fecha', 'periodo', 'fechacierre']:
                if col_fecha is None: col_fecha = c_idx
            elif norm in ['moneda', 'currency']:
                if col_moneda is None: col_moneda = c_idx

        records = []
        periodos = []

        for r_idx in range(header_row_idx + 1, len(grid)):
            row = grid[r_idx]
            has_data = any(row[c] is not None and str(row[c]).strip() != '' for c in canon_map.values() if c < len(row))
            if not has_data:
                continue

            period_name = None
            if col_fecha is not None and col_fecha < len(row) and row[col_fecha]:
                period_name = str(row[col_fecha]).strip()
            if not period_name:
                period_name = f"Periodo_{len(records) + 1}"

            if col_moneda is not None and col_moneda < len(row) and row[col_moneda] and not self._metadata.moneda:
                self._metadata.moneda = str(row[col_moneda]).strip().upper()

            periodos.append(period_name)
            rec: Dict[str, Any] = {'Periodo': period_name}
            for canon, c_idx in canon_map.items():
                val = row[c_idx] if c_idx < len(row) else None
                rec[canon] = clean_number(val)
            records.append(rec)

        if not records:
            raise InvalidFormatError("Se identificaron cabeceras contables horizontales, pero no se hallaron filas con valores numéricos.")

        df = pd.DataFrame(records).set_index('Periodo')
        self._metadata.periodos = periodos
        return df

    def _extract_vertical(self, grid: List[List[Any]], account_col_idx: int, canon_map: Dict[str, int]) -> pd.DataFrame:
        """Extrae estados financieros en formato vertical (filas = cuentas, columnas = períodos)."""
        min_account_row = min(canon_map.values())
        period_header_row_idx = max(0, min_account_row - 1)
        header_row = grid[period_header_row_idx]

        num_cols = max(len(r) for r in grid)
        period_cols: List[Tuple[int, str]] = []
        for c in range(account_col_idx + 1, num_cols):
            val = header_row[c] if c < len(header_row) else None
            has_nums = any(grid[r][c] is not None and str(grid[r][c]).strip() != '' for r in canon_map.values() if c < len(grid[r]))
            if has_nums:
                p_name = str(val).strip() if val else f"Periodo_{len(period_cols) + 1}"
                period_cols.append((c, p_name))

        if not period_cols:
            raise InvalidFormatError("No se encontraron columnas de períodos contables con datos numéricos válidos a la derecha de las cuentas.")

        records = []
        periodos = []
        for c_idx, p_name in period_cols:
            periodos.append(p_name)
            rec: Dict[str, Any] = {'Periodo': p_name}
            for canon, r_idx in canon_map.items():
                val = grid[r_idx][c_idx] if c_idx < len(grid[r_idx]) else None
                rec[canon] = clean_number(val)
            records.append(rec)

        df = pd.DataFrame(records).set_index('Periodo')
        self._metadata.periodos = periodos
        return df

    # --------------------------------------------------------------------------
    # FASE 2: TRANSFORMACIÓN, FALLBACK Y VALIDACIÓN (Transform)
    # --------------------------------------------------------------------------

    def _validate_and_sanitize(self) -> None:
        """Valida que existan las cuentas indispensables, aplica fallbacks y verifica la consistencia contable."""
        mandatory = ['Activo_Circulante', 'Pasivo_Circulante', 'Activo_Total', 'Pasivo_Total', 'Patrimonio_Neto', 'Ingresos_Netos']
        missing = [c for c in mandatory if c not in self._accounts_df.columns]
        if missing:
            raise MissingAccountError(
                f"Faltan cuentas canónicas obligatorias para el cálculo ML: {missing}. "
                f"Cuentas identificadas: {list(self._accounts_df.columns)}."
            )

        # Imputar 0.0 para cuentas no encontradas de flujo/gasto no críticas
        for opt_acc in ['Utilidades_Retenidas', 'Flujo_Operacional', 'EBIT', 'Ganancia_Antes_Impuestos', 'Costos_Financieros']:
            if opt_acc not in self._accounts_df.columns:
                self._accounts_df[opt_acc] = 0.0

        # Regla Fallback de EBIT: Ganancia antes de impuestos + Costos financieros
        for p in self._accounts_df.index:
            ebit_val = self._accounts_df.loc[p, 'EBIT']
            if pd.isna(ebit_val) or ebit_val == 0.0:
                ebt = self._accounts_df.loc[p, 'Ganancia_Antes_Impuestos']
                cf = self._accounts_df.loc[p, 'Costos_Financieros']
                if ebt != 0.0 or cf != 0.0:
                    self._accounts_df.loc[p, 'EBIT'] = ebt + cf
                    self._ebit_fallback_used = True
                    self._warnings.append(
                        f"Período '{p}': EBIT no encontrado directamente. Calculado mediante regla fallback: "
                        f"Ganancia Antes de Impuestos (${ebt:,.0f}) + Costos Financieros (${cf:,.0f}) = ${ebt+cf:,.0f}."
                    )

        # Reglas de Validación Contable
        for p in self._accounts_df.index:
            at = float(self._accounts_df.loc[p, 'Activo_Total'])
            pt = float(self._accounts_df.loc[p, 'Pasivo_Total'])
            pn = float(self._accounts_df.loc[p, 'Patrimonio_Neto'])
            ac = float(self._accounts_df.loc[p, 'Activo_Circulante'])
            pc = float(self._accounts_df.loc[p, 'Pasivo_Circulante'])

            # 1. Validar Activo_Total > 0
            if at <= 0:
                raise ETLValidationError(
                    f"Violación contable crítica en período '{p}': Activo Total debe ser estrictamente mayor a 0 (encontrado: ${at:,.0f})."
                )

            # 2. Comprobar Ecuación Patrimonial Fundamental (|Activo - (Pasivo + Patrimonio)| / Activo <= 5%)
            desbalance = abs(at - (pt + pn))
            desbalance_pct = desbalance / at
            cuadrado = desbalance_pct <= 0.05
            self._ecuacion_patrimonial[p] = {
                'activo_total': at,
                'pasivo_total': pt,
                'patrimonio_neto': pn,
                'desbalance': desbalance,
                'desbalance_pct': round(desbalance_pct, 4),
                'cuadrado': cuadrado
            }
            if not cuadrado:
                self._warnings.append(
                    f"Advertencia de desbalance contable en '{p}': |Activo - (Pasivo + Patrimonio)| / Activo = {desbalance_pct:.2%} "
                    f"(diferencia de ${desbalance:,.0f}, supera la tolerancia contable del 5.00%)."
                )

            # 3. Detección de Quiebra / Insolvencia Técnica
            if pn <= 0:
                self._warnings.append(
                    f"Alerta de Insolvencia Técnica en '{p}': Patrimonio Neto menor o igual a cero (${pn:,.0f}). "
                    f"Razón de Leverage fijada en tope de contención de 10.0 según diseño del modelo predictivo."
                )

            # 4. Inconsistencia de subcuentas
            if ac > at:
                self._warnings.append(
                    f"Inconsistencia en '{p}': Activo Circulante (${ac:,.0f}) excede al Activo Total (${at:,.0f})."
                )
            if pc > pt:
                self._warnings.append(
                    f"Inconsistencia en '{p}': Pasivo Circulante (${pc:,.0f}) excede al Pasivo Total (${pt:,.0f})."
                )

    # --------------------------------------------------------------------------
    # FASE 3: CÁLCULO DE LOS 7 RATIOS FINANCIEROS ML
    # --------------------------------------------------------------------------

    def _compute_ml_features(self) -> pd.DataFrame:
        """
        Calcula las 7 variables adimensionales con contención numérica estricta:
        V1: Razón Corriente (Tope 10.0)
        V2: Capital de Trabajo / Activos
        V3: Leverage Total (Tope 10.0 si PN <= 0 o pt/pn > 10.0)
        V4: ROA Operacional (EBIT / Activo Total)
        V5: Margen Operacional (Acotado [-1.0, 1.0])
        V6: Rotación de Activos (Tope 10.0)
        V7: Volatilidad de Flujo de Caja
        """
        features: List[Dict[str, Any]] = []
        n_periods = len(self._accounts_df)
        flujos = self._accounts_df['Flujo_Operacional'].tolist()
        ingresos_list = self._accounts_df['Ingresos_Netos'].tolist()

        # V7: Volatilidad / Flujo de Caja
        if n_periods >= 2:
            std_flujo = float(np.std(flujos, ddof=1))
            mean_ing = float(np.mean(ingresos_list))
            volatilidad = round(std_flujo / mean_ing, 4) if mean_ing > 0 else 0.0
        else:
            at_primero = float(self._accounts_df['Activo_Total'].iloc[0])
            flujo_primero = float(flujos[0])
            volatilidad = round(abs(flujo_primero / at_primero), 4) if at_primero > 0 else self.neutral_v7

        for p in self._accounts_df.index:
            ac = float(self._accounts_df.loc[p, 'Activo_Circulante'])
            pc = float(self._accounts_df.loc[p, 'Pasivo_Circulante'])
            at = float(self._accounts_df.loc[p, 'Activo_Total'])
            pt = float(self._accounts_df.loc[p, 'Pasivo_Total'])
            pn = float(self._accounts_df.loc[p, 'Patrimonio_Neto'])
            ing = float(self._accounts_df.loc[p, 'Ingresos_Netos'])
            ebit = float(self._accounts_df.loc[p, 'EBIT'])

            # V1: Razón Corriente (Activo Circulante / Pasivo Circulante)
            if pc <= 0:
                v1 = 10.0
            else:
                v1 = min(max(0.0, ac / pc), 10.0)

            # V2: Capital de Trabajo / Activos ((AC - PC) / AT)
            v2 = (ac - pc) / at

            # V3: Leverage Total (Pasivo Total / Patrimonio Neto)
            if pn <= 0:
                v3 = 10.0  # Insolvencia Técnica
            else:
                v3 = min(max(0.0, pt / pn), 10.0)

            # V4: ROA Operacional (EBIT / Activo Total)
            v4 = ebit / at

            # V5: Margen Operacional (EBIT / Ingresos Netos)
            if ing <= 0:
                v5 = -1.0 if ebit < 0 else 0.0
            else:
                v5 = float(np.clip(ebit / ing, -1.0, 1.0))

            # V6: Rotación de Activos (Ingresos Netos / Activo Total)
            v6 = min(max(0.0, ing / at), 10.0)

            # V7: Volatilidad de Flujo de Caja
            v7 = volatilidad

            features.append({
                'periodo': p,
                'razon_corriente': round(v1, 4),
                'capital_trabajo_sobre_activos': round(v2, 4),
                'leverage_total': round(v3, 4),
                'roa_operacional': round(v4, 4),
                'margen_operacional': round(v5, 4),
                'rotacion_activos': round(v6, 4),
                'volatilidad_flujo_caja': round(v7, 4),
            })

        df_feat = pd.DataFrame(features).set_index('periodo')
        # Garantizar orden estricto de columnas canónicas
        return df_feat[FEATURE_COLUMNS]

    # --------------------------------------------------------------------------
    # FASE 4: ENTREGA Y REPORTES (Load)
    # --------------------------------------------------------------------------

    def get_features_df(self) -> pd.DataFrame:
        """
        Retorna el DataFrame final con las 7 razones financieras normalizadas,
        listo para ser consumido directamente por el modelo predictivo de Machine Learning.
        """
        return self._features_df.copy()

    def get_audit_report(self) -> Dict[str, Any]:
        """
        Retorna un informe de auditoría exhaustivo que contiene:
        - Metadatos identificatorios de la empresa.
        - Cuentas contables originales homologadas y extraídas.
        - Verificación de la ecuación patrimonial (Activo = Pasivo + Patrimonio).
        - Alertas operacionales y contables (warnings de desbalance, quiebra técnica, fallbacks).
        - Resumen ejecutivo.
        """
        meta_dict = asdict(self._metadata)
        return {
            'metadata': meta_dict,
            'metadatos': meta_dict,
            'layout_detectado': self._metadata.formato_detectado,
            'cuentas_extraidas': self._accounts_df.to_dict(orient='index'),
            'ecuacion_patrimonial': self._ecuacion_patrimonial,
            'alertas': self._warnings,
            'advertencias': self._warnings,
            'resumen_ejecutivo': {
                'total_periodos': len(self._features_df),
                'periodos': list(self._features_df.index),
                'formato_detectado': self._metadata.formato_detectado,
                'quiebra_tecnica_detectada': any(self._accounts_df['Patrimonio_Neto'] <= 0),
                'desbalance_maximo_pct': max((p['desbalance_pct'] for p in self._ecuacion_patrimonial.values()), default=0.0),
                'ebit_fallback_utilizado': self._ebit_fallback_used,
            }
        }

    @property
    def metadata(self) -> CompanyMetadata:
        return self._metadata

    @property
    def accounts_df(self) -> pd.DataFrame:
        return self._accounts_df.copy()

    @property
    def features_df(self) -> pd.DataFrame:
        return self.get_features_df()
