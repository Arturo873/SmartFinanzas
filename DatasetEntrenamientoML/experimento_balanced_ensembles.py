"""
Experimento: ¿BalancedRandomForest / EasyEnsemble (los metodos que el
survey academico ranqueo primero, distintos de solo class_weight='balanced')
superan al RandomForest actual? Y de paso, se reporta F2-score y PR-AUC
ademas de F1, ya que la literatura usa esas metricas en vez de F1 puro
para este tipo de problema (ver Intento 8 en busqueda_mejora_f1.md).

Mismo dataset, split y metodologia de umbral optimo (ahora buscando el
umbral que maximiza F2, no F1, para los modelos evaluados con F2) que el
resto de experimentos.

Uso:
    python DatasetEntrenamientoML/experimento_balanced_ensembles.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    accuracy_score, recall_score, f1_score, fbeta_score, precision_score,
    average_precision_score,
)
from sklearn.preprocessing import MinMaxScaler
from imblearn.ensemble import BalancedRandomForestClassifier, EasyEnsembleClassifier

from entrenar_modelo_oficial import RATIOS_MODELO, cargar_y_mapear_dataset


def _mejor_umbral(y_true, proba_positiva, beta=1.0):
    mejor_umbral, mejor_score = 0.5, -1.0
    for umbral in np.arange(0.05, 0.96, 0.01):
        pred = (proba_positiva >= umbral).astype(int)
        score = fbeta_score(y_true, pred, beta=beta, zero_division=0)
        if score > mejor_score:
            mejor_score, mejor_umbral = score, float(umbral)
    return mejor_umbral, mejor_score


def evaluar(nombre, clf, X_train, y_train, X_test, y_test, beta=1.0):
    clf.fit(X_train, y_train)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(clf, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1)[:, 1]
    umbral_optimo, _ = _mejor_umbral(y_train, proba_cv, beta=beta)

    proba_test = clf.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral_optimo).astype(int)

    return {
        'experimento': nombre,
        'umbral_optimizado_para': f'F{beta:g}',
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 1),
        'precision': round(precision_score(y_test, y_pred, zero_division=0) * 100, 1),
        'recall': round(recall_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_test': round(f1_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f2_test': round(fbeta_score(y_test, y_pred, beta=2, zero_division=0) * 100, 1),
        'pr_auc_test': round(average_precision_score(y_test, proba_test) * 100, 1),
        'umbral': round(umbral_optimo, 2),
    }


def main():
    datos = cargar_y_mapear_dataset()
    X = datos[RATIOS_MODELO].values
    y = datos['Bankrupt'].values

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_escalado, y, test_size=0.2, random_state=42, stratify=y
    )

    resultados = []

    # Baseline actual, con umbral optimizado para F1 (igual que produccion)
    resultados.append(evaluar(
        'baseline: RandomForest class_weight=balanced (produccion, umbral->F1)',
        RandomForestClassifier(n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test, beta=1.0,
    ))

    # Mismo baseline pero con umbral optimizado para F2 (mas peso al recall)
    resultados.append(evaluar(
        'baseline: RandomForest class_weight=balanced (umbral->F2)',
        RandomForestClassifier(n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test, beta=2.0,
    ))

    # BalancedRandomForest: cada arbol del bosque se entrena sobre un
    # bootstrap balanceado (undersampling interno por arbol), distinto de
    # solo ponderar la funcion de perdida como hace class_weight
    resultados.append(evaluar(
        'BalancedRandomForest (umbral->F1)',
        BalancedRandomForestClassifier(
            n_estimators=300, max_depth=8, random_state=42, n_jobs=-1,
            sampling_strategy='all', replacement=True,
        ),
        X_train, y_train, X_test, y_test, beta=1.0,
    ))
    resultados.append(evaluar(
        'BalancedRandomForest (umbral->F2)',
        BalancedRandomForestClassifier(
            n_estimators=300, max_depth=8, random_state=42, n_jobs=-1,
            sampling_strategy='all', replacement=True,
        ),
        X_train, y_train, X_test, y_test, beta=2.0,
    ))

    # EasyEnsemble: varios AdaBoost, cada uno sobre un subset undersampled
    # distinto de la clase mayoritaria, combinados por voto
    resultados.append(evaluar(
        'EasyEnsemble (umbral->F1)',
        EasyEnsembleClassifier(n_estimators=30, random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test, beta=1.0,
    ))
    resultados.append(evaluar(
        'EasyEnsemble (umbral->F2)',
        EasyEnsembleClassifier(n_estimators=30, random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test, beta=2.0,
    ))

    df_resultados = pd.DataFrame(resultados)
    print()
    print(df_resultados.to_string(index=False))
    df_resultados.to_csv('resultado_experimento_balanced_ensembles.csv', index=False)
    print('\nGuardado en DatasetEntrenamientoML/resultado_experimento_balanced_ensembles.csv')


if __name__ == '__main__':
    main()
