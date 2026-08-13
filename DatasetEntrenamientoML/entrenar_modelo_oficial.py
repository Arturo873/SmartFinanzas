"""
Entrena el modelo oficial de SmartFinanzas con datos reales de quiebra
(Taiwan Economic Journal, via UCI ML Repository - "Taiwanese Bankruptcy Prediction").

A diferencia del entrenamiento "por archivo subido" que hacia viewsML.py
(donde las etiquetas se generaban con la misma formula de reglas que se
queria reemplazar), aqui la etiqueta 'Bankrupt?' es el resultado real
historico de cada empresa, por lo que accuracy/recall/F1 miden algo
genuino: si el modelo predice insolvencia real, no si imita una formula.

Uso:
    python DatasetEntrenamientoML/entrenar_modelo_oficial.py

Genera:
    AppWeb/modelo_oficial/modelo_riesgo.joblib   (RandomForestClassifier)
    AppWeb/modelo_oficial/escalador_ratios.joblib (MinMaxScaler)
    AppWeb/modelo_oficial/metricas.joblib         (accuracy/recall/f1/etc.)
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.preprocessing import MinMaxScaler

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.csv')
DIR_SALIDA = os.path.join(RAIZ_PROYECTO, 'AppWeb', 'modelo_oficial')
os.makedirs(DIR_SALIDA, exist_ok=True)

# Orden fijo: debe coincidir exactamente con AppWeb/views.py -> calcular_ratios_liquidez()
# Las 2 ultimas (rentabilidad_activos, capital_trabajo_sobre_activos) se agregaron
# porque en las pruebas de Colab (ver prompt_colab_mejorar_f1.md) subieron el F1
# de 36.4% a 48.4% sin necesitar columnas fuera de la plantilla de carga ya aprobada.
RATIOS_MODELO = [
    'razon_corriente',
    'prueba_acida',
    'endeudamiento_corto_plazo',
    'solvencia_general',
    'cobertura_operacional',
    'rentabilidad_activos',
    'capital_trabajo_sobre_activos',
]

# Tope de clipping para las columnas del dataset de Taiwan que traen
# outliers extremos de captura de datos (algunas filas llegan a valores
# de hasta 2.7e9 en 'Current Ratio'). Sin este recorte, el escalador
# quedaria dominado por un puñado de filas y aplastaria el rango normal.
TOPE_RATIO = 10.0


def cargar_y_mapear_dataset() -> pd.DataFrame:
    df = pd.read_csv(RUTA_DATASET)
    df.columns = [c.strip() for c in df.columns]

    ratios = pd.DataFrame(index=df.index)
    ratios['razon_corriente'] = df['Current Ratio'].clip(upper=TOPE_RATIO)
    ratios['prueba_acida'] = df['Quick Ratio'].clip(upper=TOPE_RATIO)
    ratios['endeudamiento_corto_plazo'] = df['Current Liabilities/Liability']

    debt_ratio = df['Debt ratio %'].replace(0, np.nan)
    ratios['solvencia_general'] = (1.0 / debt_ratio).clip(upper=TOPE_RATIO).fillna(TOPE_RATIO)

    ratios['cobertura_operacional'] = df['Operating Funds to Liability']

    # Nota: estas 2 columnas de Taiwan ya vienen normalizadas 0-1 por los
    # autores del dataset (igual que 'Operating Funds to Liability' arriba),
    # no son la razon cruda utilidad_neta/activo_total. Es una limitacion
    # conocida del dataset: el orden relativo entre empresas se preserva
    # (por eso sirve para que el arbol aprenda umbrales de separacion), pero
    # la escala no es identica a la razon cruda que calculara Django en
    # produccion. Documentado en prompt_colab_mejorar_f1.md.
    ratios['rentabilidad_activos'] = df['Net Income to Total Assets']
    ratios['capital_trabajo_sobre_activos'] = df['Working Capital to Total Assets']

    ratios['Bankrupt'] = df['Bankrupt?']
    return ratios


def _mejor_umbral_f1(y_true, proba_positiva) -> float:
    """Recorre umbrales candidatos y devuelve el que maximiza F1."""
    mejor_umbral, mejor_f1 = 0.5, -1.0
    for umbral in np.arange(0.05, 0.96, 0.01):
        pred = (proba_positiva >= umbral).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > mejor_f1:
            mejor_f1, mejor_umbral = f1, float(umbral)
    return mejor_umbral, mejor_f1


def entrenar():
    datos = cargar_y_mapear_dataset()

    X = datos[RATIOS_MODELO].values
    y = datos['Bankrupt'].values

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_escalado, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # Umbral optimo de F1 buscado con validacion cruzada de 5 folds SOLO
    # sobre el train set (nunca se toca el test set aqui), para no
    # sobreajustar el umbral al conjunto de prueba.
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(
        clf, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1
    )[:, 1]
    umbral_optimo, f1_cv = _mejor_umbral_f1(y_train, proba_cv)

    # Metricas finales sobre el test set (20%, nunca visto durante el ajuste
    # de umbral), aplicando ese mismo umbral.
    proba_test = clf.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral_optimo).astype(int)

    metricas = {
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 1),
        'precision': round(precision_score(y_test, y_pred, zero_division=0) * 100, 1),
        'recall': round(recall_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_score': round(f1_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_score_cv_train': round(f1_cv * 100, 1),
        'umbral_clasificacion': round(umbral_optimo * 100, 1),
        'total_empresas_entrenamiento': int(len(datos)),
        'fuente_dataset': 'Taiwan Economic Journal (UCI ML Repository / Kaggle) - Bankrupt companies 1999-2009',
        'features_orden': RATIOS_MODELO,
    }

    print('Métricas sobre el conjunto de prueba (20%), con umbral óptimo de F1:')
    for k, v in metricas.items():
        print(f'  {k}: {v}')

    joblib.dump(clf, os.path.join(DIR_SALIDA, 'modelo_riesgo.joblib'))
    joblib.dump(escalador, os.path.join(DIR_SALIDA, 'escalador_ratios.joblib'))
    joblib.dump(metricas, os.path.join(DIR_SALIDA, 'metricas.joblib'))
    print(f'\nModelo, escalador y métricas guardados en {DIR_SALIDA}')


if __name__ == '__main__':
    entrenar()
