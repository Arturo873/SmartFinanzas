"""Las 8 variables del modelo predictivo (tablero Miro "SmartFinanzas",
Requerimientos v8). Fuentes y umbrales: documentacion/fuentes_modelo_ml.md.

Este módulo es la única definición de las fórmulas: lo usan tanto el ETL de
Django (RF-10) como los scripts de entrenamiento sintético
(DatasetSinteticoEntrenamientoML), para que el modelo vea en producción
exactamente las mismas variables con las que se entrenó. No depende de Django
(RNF-09).
"""
import numpy as np

# Topes para que los cocientes con denominadores cercanos a cero no generen
# valores extremos que el modelo nunca vio al entrenar. Son decisiones de
# diseño, elegidas holgadas respecto de los umbrales de la literatura.
RAZON_CORRIENTE_MAXIMA = 10.0
# Riquelme (2018, p. 106) califica un Pasivo/Patrimonio > 5 como "bastante
# alto"; el tope es el doble. Patrimonio <= 0 significa pasivos mayores que
# activos (insolvencia contable, p. 116), así que toma el valor de riesgo máximo.
LEVERAGE_MAXIMO = 10.0
MARGEN_OPERACIONAL_LIMITE = 1.0
ROTACION_ACTIVOS_MAXIMA = 10.0

# V7 (RNF-10): cierres de caja confirmados mínimos para calcular la volatilidad.
MINIMO_CIERRES_VOLATILIDAD = 20
# Valor que toma V7 cuando no hay cierres suficientes. Se fija en la Fase 4
# con la mediana de la clase solvente del dataset sintético, para que "sin
# datos" no empuje la predicción hacia ninguna clase.
VOLATILIDAD_NEUTRA = None

VARIABLES_MODELO = [
    # clave, nombre para el usuario, grupo (RF-05)
    ('razon_corriente', 'Razón Corriente', 'liquidez'),
    ('capital_trabajo_sobre_activos', 'Capital de Trabajo sobre Activos', 'liquidez'),
    ('leverage_total', 'Leverage Total (Pasivo / Patrimonio)', 'endeudamiento'),
    ('roa_operacional', 'ROA Operacional (EBIT / Activo Total)', 'rentabilidad'),
    ('margen_operacional', 'Margen Operacional', 'rentabilidad'),
    ('rotacion_activos', 'Rotación de Activos', 'eficiencia'),
    ('volatilidad_flujo_caja', 'Volatilidad del Flujo de Caja', 'flujo de caja'),
    ('var_pib', 'Variación anual del PIB (%)', 'contexto económico'),
    ('tasa_captacion_uf', 'Tasa de captación UF 90 días-1 año (%)', 'contexto económico'),
    ('tipo_cambio_real', 'Índice de Tipo de Cambio Real', 'contexto económico'),
]

CLAVES_MODELO = [clave for clave, _, _ in VARIABLES_MODELO]

# V8 es una sola variable (contexto macroeconómico) medida con los 3
# indicadores de Zurita (2008). El Random Forest recibe cada indicador como
# una entrada propia: 8 variables = 10 entradas. Ante el usuario (RF-03,
# RF-10) los 3 se muestran juntos como V8.
INDICADORES_V8 = ('var_pib', 'tasa_captacion_uf', 'tipo_cambio_real')
CLAVE_V8 = 'contexto_macroeconomico'
NOMBRE_V8 = 'Contexto Macroeconómico'
GRUPO_V8 = 'contexto económico'


def _dividir(numerador, denominador):
    return numerador / denominador if denominador > 0 else None


def calcular_variables_financieras(fila: dict) -> dict:
    """V1 a V6 a partir de una fila de la plantilla de carga (RF-08)."""
    activo_corriente = float(fila['Activo_Circulante'])
    pasivo_corriente = float(fila['Pasivo_Circulante'])
    activo_total = float(fila['Activo_Total'])
    pasivo_total = float(fila['Pasivo_Total'])
    patrimonio = float(fila['Patrimonio_Neto'])
    ingresos = float(fila['Ingresos_Netos'])
    ebit = float(fila['EBIT'])

    razon_corriente = _dividir(activo_corriente, pasivo_corriente)
    if razon_corriente is None:
        razon_corriente = RAZON_CORRIENTE_MAXIMA

    leverage = _dividir(pasivo_total, patrimonio)
    if leverage is None:
        leverage = LEVERAGE_MAXIMO

    margen = _dividir(ebit, ingresos)
    if margen is None:
        # Sin ingresos: un EBIT negativo es el peor margen posible.
        margen = -MARGEN_OPERACIONAL_LIMITE if ebit < 0 else 0.0

    activo_total_seguro = activo_total if activo_total > 0 else 1e-6
    return {
        'razon_corriente': min(razon_corriente, RAZON_CORRIENTE_MAXIMA),
        'capital_trabajo_sobre_activos': (activo_corriente - pasivo_corriente) / activo_total_seguro,
        'leverage_total': min(leverage, LEVERAGE_MAXIMO),
        'roa_operacional': ebit / activo_total_seguro,
        'margen_operacional': float(np.clip(margen, -MARGEN_OPERACIONAL_LIMITE, MARGEN_OPERACIONAL_LIMITE)),
        'rotacion_activos': min(ingresos / activo_total_seguro, ROTACION_ACTIVOS_MAXIMA),
    }


def calcular_volatilidad_flujo_caja(flujos_netos_diarios, ingresos_diarios):
    """V7: desviación estándar del flujo neto diario dividida por el ingreso
    promedio diario (RNF-10), para comparar empresas de distinto tamaño.

    Devuelve None si hay menos de MINIMO_CIERRES_VOLATILIDAD cierres o no
    hubo ingresos; quien la use debe reemplazarlo por VOLATILIDAD_NEUTRA.
    """
    flujos = np.asarray(flujos_netos_diarios, dtype=float)
    ingresos = np.asarray(ingresos_diarios, dtype=float)
    if len(flujos) < MINIMO_CIERRES_VOLATILIDAD or ingresos.mean() <= 0:
        return None
    return float(flujos.std(ddof=1) / ingresos.mean())


# Corte de la zona de insolvencia del Z''EM (Riquelme, 2018, p. 55).
UMBRAL_ZEM_INSOLVENCIA = 1.10


def calcular_zem_altman(fila: dict) -> float:
    """Z-score de Altman para mercados emergentes (Z''EM): Altman (2000) quitó
    la rotación de activos (X5) para minimizar el efecto de la industria en
    empresas no manufactureras, y Altman et al. (2017) agregaron la constante
    3,25 (citados en Riquelme, 2018, pp. 54-55). Z''EM < 1,10 = alta
    probabilidad de insolvencia. Se usa para etiquetar los datos de
    entrenamiento (RNF-08), no como variable del modelo.
    """
    activo_total = float(fila['Activo_Total'])
    pasivo_total = float(fila['Pasivo_Total'])
    x1 = (float(fila['Activo_Circulante']) - float(fila['Pasivo_Circulante'])) / activo_total
    x2 = float(fila['Utilidades_Retenidas']) / activo_total
    x3 = float(fila['EBIT']) / activo_total
    # Sin pasivos, Patrimonio/Pasivo tiende a infinito (máxima solvencia); se acota al mismo tope.
    x4 = float(fila['Patrimonio_Neto']) / pasivo_total if pasivo_total > 0 else LEVERAGE_MAXIMO
    return 3.25 + 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4


def calcular_variables_modelo(fila: dict, contexto_macro: dict, volatilidad_flujo_caja=None) -> dict:
    """Las 10 entradas del modelo (8 variables; V8 son 3 indicadores) en el orden de CLAVES_MODELO."""
    variables = calcular_variables_financieras(fila)
    variables['volatilidad_flujo_caja'] = (
        volatilidad_flujo_caja if volatilidad_flujo_caja is not None else VOLATILIDAD_NEUTRA
    )
    for clave in INDICADORES_V8:
        variables[clave] = contexto_macro[clave]
    return {clave: variables[clave] for clave in CLAVES_MODELO}
