"""Contexto macroeconómico (V8) desde la Base de Datos Estadísticos del Banco
Central de Chile (RF-01, RNF-09).

Usa las tres variables de Zurita (2008): variación anual del PIB, tasa de
interés y tipo de cambio real. Las series se descargan de las tablas públicas
del BDE (no requieren registro) y se guardan en un CSV versionado, para que la
predicción no dependa de la red (RNF-05) y el entrenamiento sintético
(DatasetSinteticoEntrenamientoML) use exactamente los mismos datos.

Actualizar el CSV:  python manage.py actualizar_datos_macro
"""
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

RUTA_CSV_MACRO = os.path.join(os.path.dirname(__file__), 'datos_macro', 'indicadores_macro.csv')

BDE_BASE = 'https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/'

# columna: (cuadro BDE, tipo de cálculo, inicio del nombre de la fila)
SERIES_MACRO = {
    # Variación % respecto del mismo trimestre del año anterior (Zurita usa
    # "la tasa de crecimiento del PIB trimestral a 4 trimestres").
    'var_pib': (
        'CAP_ESTADIST_MACRO/MN_EST_MACRO_IV/PEM_ACTyDDA_IndMacT_2_2018/',
        'YTYPCT',
        'PIB, volumen (miles de millones $ encadenado)',
    ),
    # Captación reajustable en UF de 90 días a 1 año; Zurita usa captación
    # en UF de 30 a 365 días, y el BDE no publica el tramo de 30-89 días en UF.
    'tasa_captacion_uf': (
        'CAP_TASA_INTERES/MN_TASA_INTERES_09/TSF_35/T532',
        'NONE',
        '90 días a 1 año - tasa',
    ),
    'tipo_cambio_real': (
        'CAP_TIPO_CAMBIO/MN_TIPO_CAMBIO4/TCB_531_IND_TCRYCOMP/TCB_531',
        'NONE',
        'Índice de tipo de cambio real - TCR',
    ),
}

COLUMNAS_MACRO = list(SERIES_MACRO)

_ROMANO_A_TRIMESTRE = {'I': 1, 'II': 2, 'III': 3, 'IV': 4}

_cache_csv = {}


def _encabezado_a_trimestre(texto: str):
    """'III.2026' -> '2026-Q3' (mismo formato que la columna Periodo de la plantilla)."""
    m = re.fullmatch(r'(I{1,3}|IV)\.(\d{4})', texto.strip())
    if not m:
        return None
    return f'{m.group(2)}-Q{_ROMANO_A_TRIMESTRE[m.group(1)]}'


def _a_numero(texto: str):
    texto = texto.strip().replace('.', '').replace(',', '.')
    try:
        return float(texto)
    except ValueError:
        return None


def _descargar_serie(cuadro: str, calculo: str, nombre_fila: str, desde: int, hasta: int) -> pd.Series:
    url = (f'{BDE_BASE}{cuadro}?cbFechaInicio={desde}&cbFechaTermino={hasta}'
           f'&cbFrecuencia=QUARTERLY&cbCalculo={calculo}')
    resp = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    resp.raise_for_status()
    filas = BeautifulSoup(resp.text, 'lxml').find_all('tr')

    trimestres = [_encabezado_a_trimestre(c.get_text(strip=True)) for c in filas[0].find_all(['td', 'th'])]
    for fila in filas[1:]:
        celdas = [c.get_text(' ', strip=True) for c in fila.find_all(['td', 'th'])]
        if len(celdas) > 1 and celdas[1].startswith(nombre_fila):
            valores = {t: _a_numero(v) for t, v in zip(trimestres, celdas) if t}
            return pd.Series(valores, dtype='float64').dropna()
    raise ValueError(f'No se encontró la serie "{nombre_fila}" en el cuadro {cuadro}')


def descargar_indicadores_macro(desde: int = 2009, hasta: int = None) -> pd.DataFrame:
    hasta = hasta or pd.Timestamp.today().year
    df = pd.DataFrame({
        columna: _descargar_serie(cuadro, calculo, nombre_fila, desde, hasta)
        for columna, (cuadro, calculo, nombre_fila) in SERIES_MACRO.items()
    })
    df.index.name = 'trimestre'
    return df.sort_index()


def actualizar_csv_macro(desde: int = 2009) -> pd.DataFrame:
    df = descargar_indicadores_macro(desde)
    os.makedirs(os.path.dirname(RUTA_CSV_MACRO), exist_ok=True)
    df.to_csv(RUTA_CSV_MACRO, float_format='%.4f')
    _cache_csv.clear()
    return df


def cargar_indicadores_macro() -> pd.DataFrame:
    if 'df' not in _cache_csv:
        _cache_csv['df'] = pd.read_csv(RUTA_CSV_MACRO, index_col='trimestre')
    return _cache_csv['df']


def obtener_contexto_macro(periodo: str) -> dict:
    """Indicadores macro del trimestre del período cargado ('2024-Q4').

    Si ese trimestre aún no tiene las tres series publicadas, usa el último
    trimestre anterior que sí las tenga, y lo informa en 'trimestre_usado'
    para mostrarlo en pantalla (RF-01).
    """
    completos = cargar_indicadores_macro().dropna(subset=COLUMNAS_MACRO)
    disponibles = completos[completos.index <= str(periodo)]
    if disponibles.empty:
        disponibles = completos.iloc[:1]
    trimestre_usado = disponibles.index[-1]
    fila = disponibles.iloc[-1]
    return {
        **{col: float(fila[col]) for col in COLUMNAS_MACRO},
        'trimestre_usado': trimestre_usado,
        'es_periodo_exacto': trimestre_usado == str(periodo),
    }
