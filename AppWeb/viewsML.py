import hashlib
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score

MODELOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'modelos')
os.makedirs(MODELOS_DIR, exist_ok=True)

FEATURES = [
    'Activo_Circulante', 'Pasivo_Circulante', 'Efectivo_Equivalentes',
    'Inventarios', 'Activo_Total', 'Pasivo_Total',
    'Patrimonio_Neto', 'Utilidad_Neta'
]


def calcular_ratios_liquidez(row: dict):
    activo_circulante = row.get('Activo_Circulante', 0)
    pasivo_circulante = row.get('Pasivo_Circulante', 0)
    inventario = row.get('Inventarios', 0)
    caja_y_bancos = row.get('Efectivo_Equivalentes', 0)
    flujo_caja_operativo = row.get('Utilidad_Neta', 0)
    pasivo_total = row.get('Pasivo_Total', 0)
    activo_total = row.get('Activo_Total', 0)

    eps = 1e-6
    denom = pasivo_circulante if pasivo_circulante > 0 else eps

    return {
        'razon_corriente': activo_circulante / denom,
        'prueba_acida': (activo_circulante - inventario) / denom,
        'ratio_caja': caja_y_bancos / denom,
        'cobertura_operacional': flujo_caja_operativo / denom,
        'capital_trabajo': activo_circulante - pasivo_circulante,
        'endeudamiento_corto_plazo': pasivo_circulante / (pasivo_total if pasivo_total > 0 else eps),
        'solvencia_general': activo_total / (pasivo_total if pasivo_total > 0 else eps),
    }


def _score_razon_corriente(rc):
    if rc <= 0.5: return 25
    elif rc <= 1.0: return 20
    elif rc <= 1.5: return 14
    elif rc <= 2.0: return 8
    return 3

def _score_prueba_acida(pa):
    if pa <= 0.5: return 20
    elif pa <= 1.0: return 14
    return 4

def _score_endeudamiento(ecp):
    if ecp >= 0.7: return 25
    elif ecp >= 0.5: return 18
    elif ecp >= 0.3: return 10
    return 4

def _score_solvencia(sg):
    if sg <= 1.0: return 20
    elif sg <= 1.5: return 14
    elif sg <= 2.0: return 8
    return 3

def _score_cobertura(co):
    if co <= -0.5: return 10
    elif co < 0: return 7
    elif co < 0.1: return 4
    return 1


def calcular_score_compuesto(ratios: dict) -> float:
    score = (
        _score_razon_corriente(ratios.get('razon_corriente', 1))
        + _score_prueba_acida(ratios.get('prueba_acida', 1))
        + _score_endeudamiento(ratios.get('endeudamiento_corto_plazo', 0.5))
        + _score_solvencia(ratios.get('solvencia_general', 1))
        + _score_cobertura(ratios.get('cobertura_operacional', 0))
    )
    return min(max(round(score, 1), 0), 100)


ANALISIS_REGISTRO = [
    {
        'key': 'razon_corriente',
        'label': 'Razón Corriente',
        'score_fn': _score_razon_corriente,
        'ideal': 3,
        'max_puntaje': 25,
        'format_val': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Tus activos circulantes equivalen a {v:.2f} veces tus deudas a corto plazo. '
            'Un valor inferior a 2.0 indica que podrías tener dificultades para cubrir tus obligaciones inmediatas.'
        ),
        'consejo': (
            'Aumenta tu efectivo disponible, reduce cuentas por cobrar o renegocia plazos con proveedores '
            'para mejorar tu liquidez corriente.'
        ),
    },
    {
        'key': 'prueba_acida',
        'label': 'Prueba Ácida',
        'score_fn': _score_prueba_acida,
        'ideal': 4,
        'max_puntaje': 20,
        'format_val': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Sin considerar inventarios, tus activos líquidos cubren {v:.2f} veces tus deudas a corto plazo. '
            'Un valor menor a 1.0 indica dependencia de tus inventarios para pagar deudas.'
        ),
        'consejo': (
            'Reduce tus inventarios de lenta rotación o convierte cuentas por cobrar en efectivo '
            'para mejorar tu liquidez más exigente.'
        ),
    },
    {
        'key': 'endeudamiento_corto_plazo',
        'label': 'Endeudamiento C/P',
        'score_fn': _score_endeudamiento,
        'ideal': 4,
        'max_puntaje': 25,
        'format_val': lambda v: f'{v:.2f}',
        'explicacion': lambda v: (
            f'El {v:.1%} de tu pasivo total vence en el corto plazo. '
            'Una concentración alta de deuda a corto plazo incrementa el riesgo de refinanciamiento.'
        ),
        'consejo': (
            'Reestructura parte de tu deuda a largo plazo para aliviar la presión de pagos inmediatos '
            'y mejorar tu perfil de vencimientos.'
        ),
    },
    {
        'key': 'solvencia_general',
        'label': 'Solvencia General',
        'score_fn': _score_solvencia,
        'ideal': 3,
        'max_puntaje': 20,
        'format_val': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Tus activos totales respaldan {v:.2f} veces tus deudas totales. '
            'Un valor cercano a 1.0 indica que una caída en el valor de tus activos podría dejar sin respaldo a tus acreedores.'
        ),
        'consejo': (
            'Aumenta tu patrimonio mediante capitalización de utilidades o aportes de socios, '
            'y reduce tu dependencia de financiamiento externo.'
        ),
    },
    {
        'key': 'cobertura_operacional',
        'label': 'Cobertura Operacional',
        'score_fn': _score_cobertura,
        'ideal': 1,
        'max_puntaje': 10,
        'format_val': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Tu utilidad neta representa {v:.2f} veces tus deudas a corto plazo. '
            'Un valor negativo significa que tus operaciones no generan suficiente flujo para cubrir obligaciones.'
        ),
        'consejo': (
            'Revisa tu estructura de costos y gastos operacionales. Busca mejorar márgenes '
            'o aumentar ingresos para generar flujo operacional positivo sostenido.'
        ),
    },
]


def analizar_contribucion_riesgo(ratios: dict) -> list:
    resultados = []
    for regla in ANALISIS_REGISTRO:
        v = ratios.get(regla['key'], 0)
        puntaje = regla['score_fn'](v)
        impacto = puntaje - regla['ideal']
        resultados.append({
            'key': regla['key'],
            'label': regla['label'],
            'valor': regla['format_val'](v),
            'valor_raw': round(v, 4),
            'puntaje': puntaje,
            'max_puntaje': regla.get('max_puntaje', 25),
            'impacto': impacto,
            'explicacion': regla['explicacion'](v),
            'consejo': regla['consejo'],
        })
    return sorted(resultados, key=lambda r: r['impacto'], reverse=True)[:3]


RECOMENDACIONES_POR_ALERTA = {
    'Verde': {
        'titulo': 'Riesgo bajo: mantén el control',
        'mensaje': (
            'Tu situación financiera es sólida. Mantén el monitoreo periódico de tus ratios de liquidez '
            'y endeudamiento para conservar este nivel de riesgo.'
        ),
    },
    'Amarillo': {
        'titulo': 'Riesgo moderado: actúa de forma preventiva',
        'mensaje': (
            'Existen señales de alerta en algunos indicadores. Revisa los factores destacados abajo y aplica '
            'las recomendaciones asociadas antes de que el riesgo escale a un nivel crítico.'
        ),
    },
    'Rojo': {
        'titulo': 'Riesgo crítico: se requiere acción inmediata',
        'mensaje': (
            'Tu empresa presenta un riesgo alto de insolvencia. Prioriza de inmediato las recomendaciones '
            'de los factores con mayor impacto y considera asesoría financiera especializada.'
        ),
    },
}


def obtener_recomendacion_general(color: str) -> dict:
    return RECOMENDACIONES_POR_ALERTA.get(color, RECOMENDACIONES_POR_ALERTA['Amarillo'])


def ruta_cache_modelo(ruta_csv: str) -> str:
    """Cada archivo cargado (identificado por ruta + fecha de modificación) tiene su
    propio modelo serializado, para no reentrenar en cada click de Ejecutar Predicción."""
    firma = f'{os.path.abspath(ruta_csv)}:{os.path.getmtime(ruta_csv)}'
    nombre = hashlib.md5(firma.encode()).hexdigest()
    return os.path.join(MODELOS_DIR, f'{nombre}.joblib')


def entrenar_modelo(ruta_csv: str) -> dict:
    """Entrena el clasificador y calcula sus métricas. Es la única función que
    reentrena desde cero; su resultado se serializa en disco vía joblib."""
    df = pd.read_csv(ruta_csv)
    n = len(df)

    if n < 4:
        return {
            'accuracy': None,
            'recall': None,
            'f1_score': None,
            'total_empresas': n,
            'umbral_clasificacion': 50,
        }

    scores = []
    for _, row in df.iterrows():
        ratios = calcular_ratios_liquidez(row.to_dict())
        scores.append(calcular_score_compuesto(ratios))

    y = (np.array(scores) >= 50).astype(int)

    X = df[FEATURES].values

    try:
        split_kwargs = dict(test_size=0.2, random_state=42)
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) > 1 and min(counts) > 1:
            split_kwargs['stratify'] = y

        X_train, X_test, y_train, y_test = train_test_split(X, y, **split_kwargs)

        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)

        accuracy = round(accuracy_score(y_test, y_pred) * 100, 1)
        recall = round(recall_score(y_test, y_pred, zero_division=0) * 100, 1)
        f1 = round(f1_score(y_test, y_pred, zero_division=0) * 100, 1)
    except Exception:
        accuracy = recall = f1 = None

    return {
        'accuracy': accuracy,
        'recall': recall,
        'f1_score': f1,
        'total_empresas': n,
        'umbral_clasificacion': 50,
    }


def obtener_metricas(ruta_csv: str) -> dict:
    """Carga las métricas del modelo ya entrenado para este archivo si existen en
    caché; si no, entrena una vez y serializa el resultado con joblib."""
    ruta_cache = ruta_cache_modelo(ruta_csv)

    if os.path.exists(ruta_cache):
        return joblib.load(ruta_cache)

    metricas = entrenar_modelo(ruta_csv)
    joblib.dump(metricas, ruta_cache)
    return metricas
