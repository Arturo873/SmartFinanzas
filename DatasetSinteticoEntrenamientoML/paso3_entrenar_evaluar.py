"""Paso 3: entrena el modelo oficial, un Random Forest desde cero (Breiman,
2001), solo con las empresas reales de entrenamiento de la CMF, y lo evalúa
(RNF-08) en la prueba real: empresas CMF que nunca se usaron al entrenar
(real_prueba.csv), con su proporción natural de insolventes (~5 %).

Como comparación (Acta CreaEmpresas 05-10-2026), entrena también un modelo con
cada dataset sintético y lo evalúa en dos conjuntos:

  a) Prueba sintética: 20 % del mismo dataset, separado antes de entrenar.
  b) La misma prueba real que el modelo oficial.

Los sintéticos no mejoraron la prueba real, por eso el modelo oficial usa solo
datos reales.

Además informa, solo como chequeo ilustrativo, la probabilidad que asigna el
modelo a las 3 empresas con quiebra real del Boletín Concursal.

El modelo oficial se guarda en AppWeb/modelo_oficial/ para que lo use el sistema.

Salidas: resultados_entrenamiento.csv y los archivos del modelo.
"""
import os
import sys
from datetime import date

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)

from AppWeb.variables_modelo import CLAVES_MODELO  # noqa: E402
from paso2_generar_sinteticos import PROPORCIONES_INSOLVENTES, SEMILLA  # noqa: E402

DIR_MODELO = os.path.join(RAIZ, 'AppWeb', 'modelo_oficial')
NOMBRE_SOLO_REALES = 'solo reales'


def nuevo_random_forest() -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=SEMILLA)


def metricas(y_real, probabilidad, umbral=0.5) -> dict:
    prediccion = (probabilidad >= umbral).astype(int)
    return {
        'accuracy': accuracy_score(y_real, prediccion),
        'f1': f1_score(y_real, prediccion, zero_division=0),
        'recall_insolvente': recall_score(y_real, prediccion, zero_division=0),
        'precision_insolvente': precision_score(y_real, prediccion, zero_division=0),
        'pr_auc': average_precision_score(y_real, probabilidad),
    }


def main():
    prueba_real = pd.read_csv(os.path.join(AQUI, 'real_prueba.csv'))
    entrenamiento_real = pd.read_csv(os.path.join(AQUI, 'real_entrenamiento.csv'))

    # Modelo oficial: solo empresas reales, con su proporción natural.
    modelo = nuevo_random_forest()
    modelo.fit(entrenamiento_real[CLAVES_MODELO], entrenamiento_real['insolvente'])
    real = metricas(prueba_real['insolvente'], modelo.predict_proba(prueba_real[CLAVES_MODELO])[:, 1])
    filas = [{'datos_entrenamiento': NOMBRE_SOLO_REALES, **{f'real_{k}': v for k, v in real.items()}}]

    # Comparación con los datasets sintéticos del Acta.
    for prop in PROPORCIONES_INSOLVENTES:
        nombre = f'{round(prop * 100)}/{round((1 - prop) * 100)}'
        dataset = pd.read_csv(os.path.join(AQUI, f'sintetico_{round(prop * 100)}_{round((1 - prop) * 100)}.csv'))
        x_ent, x_pru, y_ent, y_pru = train_test_split(
            dataset[CLAVES_MODELO], dataset['insolvente'],
            test_size=0.2, stratify=dataset['insolvente'], random_state=SEMILLA,
        )
        comparado = nuevo_random_forest()
        comparado.fit(x_ent, y_ent)
        sintetica = metricas(y_pru, comparado.predict_proba(x_pru)[:, 1])
        real_comparado = metricas(prueba_real['insolvente'], comparado.predict_proba(prueba_real[CLAVES_MODELO])[:, 1])
        filas.append({
            'datos_entrenamiento': f'sintetico {nombre}',
            **{f'real_{k}': v for k, v in real_comparado.items()},
            **{f'sintetica_{k}': v for k, v in sintetica.items()},
        })

    resultados = pd.DataFrame(filas)
    resultados.to_csv(os.path.join(AQUI, 'resultados_entrenamiento.csv'), index=False, float_format='%.4f')
    with pd.option_context('display.width', 200, 'display.max_columns', 20):
        print((resultados.set_index('datos_entrenamiento') * 100).round(1).to_string())

    print('\nChequeo ilustrativo, empresas con quiebra real (Boletín Concursal):')
    quiebras = prueba_real[prueba_real['quiebra_real_boletin'] == 1].copy()
    quiebras['probabilidad_modelo'] = modelo.predict_proba(quiebras[CLAVES_MODELO])[:, 1]
    ultimo_anio = quiebras.sort_values('anio').groupby('rut').tail(1)
    print(ultimo_anio[['razon_social', 'anio', 'zem_altman', 'insolvente', 'probabilidad_modelo']].round(2).to_string(index=False))

    solventes = entrenamiento_real[entrenamiento_real['insolvente'] == 0]
    volatilidad_neutra = float(solventes['volatilidad_flujo_caja'].median())

    # Mientras no exista el módulo de caja (RF-19 a RF-22), el sistema usa V7
    # neutra para todas las empresas: esta es la cifra realista en producción.
    sin_caja = prueba_real.assign(volatilidad_flujo_caja=volatilidad_neutra)
    real_sin_caja = metricas(sin_caja['insolvente'], modelo.predict_proba(sin_caja[CLAVES_MODELO])[:, 1])
    print('\nPrueba real con V7 neutra (sin módulo de caja):', {k: round(v * 100, 1) for k, v in real_sin_caja.items()})

    importancias = dict(zip(CLAVES_MODELO, modelo.feature_importances_.round(4)))
    print('\nImportancia de cada variable:', dict(sorted(importancias.items(), key=lambda kv: -kv[1])))

    joblib.dump(modelo, os.path.join(DIR_MODELO, 'modelo_riesgo_v11.joblib'), compress=3)
    joblib.dump({
        'version': 'v11',
        'fecha_entrenamiento': date.today().isoformat(),
        'features_orden': CLAVES_MODELO,
        'datos_entrenamiento': NOMBRE_SOLO_REALES,
        'metricas_prueba_real': {k: float(v) for k, v in real.items()},
        'metricas_prueba_real_sin_caja': {k: float(v) for k, v in real_sin_caja.items()},
        'importancias': {k: float(v) for k, v in importancias.items()},
        # Referencia de "empresa sana" para V7 sin datos de caja (RNF-10) y
        # para el panel de explicabilidad (RF-03).
        'volatilidad_neutra': volatilidad_neutra,
        'medianas_solventes': {k: float(solventes[k].median()) for k in CLAVES_MODELO},
        'total_empresas_entrenamiento': int(entrenamiento_real['rut'].nunique()),
    }, os.path.join(DIR_MODELO, 'metricas_v11.joblib'))
    print(f'\nModelo guardado en {DIR_MODELO}')


if __name__ == '__main__':
    np.random.seed(SEMILLA)
    main()
