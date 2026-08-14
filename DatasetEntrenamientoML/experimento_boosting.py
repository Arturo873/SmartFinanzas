"""
Experimento: ¿Gradient Boosting (XGBoost / HistGradientBoosting) supera al
RandomForest actual en F1, tal como sugiere la literatura (ver Intento 8)?

Mismo dataset (Taiwan, produccion), mismo split 80/20 y misma metodologia
de umbral optimo por CV de 5 folds sobre train, evaluado sobre el mismo
test set intacto -- unica variable que cambia es el algoritmo.

Uso:
    python DatasetEntrenamientoML/experimento_boosting.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier

from entrenar_modelo_oficial import (
    RATIOS_MODELO,
    cargar_y_mapear_dataset,
    _mejor_umbral_f1,
)


def evaluar(nombre, clf, X_train, y_train, X_test, y_test):
    clf.fit(X_train, y_train)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(clf, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1)[:, 1]
    umbral_optimo, f1_cv = _mejor_umbral_f1(y_train, proba_cv)
    proba_test = clf.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral_optimo).astype(int)
    return {
        'experimento': nombre,
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 1),
        'precision': round(precision_score(y_test, y_pred, zero_division=0) * 100, 1),
        'recall': round(recall_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_test': round(f1_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_cv_train': round(f1_cv * 100, 1),
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

    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    scale_pos_weight = n_neg / n_pos

    resultados = []

    resultados.append(evaluar(
        'baseline: RandomForest class_weight=balanced (produccion actual)',
        RandomForestClassifier(n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test,
    ))

    resultados.append(evaluar(
        'HistGradientBoosting class_weight=balanced',
        HistGradientBoostingClassifier(max_iter=300, max_depth=8, class_weight='balanced', random_state=42),
        X_train, y_train, X_test, y_test,
    ))

    resultados.append(evaluar(
        f'XGBoost scale_pos_weight={scale_pos_weight:.1f}',
        XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            scale_pos_weight=scale_pos_weight, eval_metric='logloss',
            random_state=42, n_jobs=-1,
        ),
        X_train, y_train, X_test, y_test,
    ))

    resultados.append(evaluar(
        'XGBoost sin scale_pos_weight (baseline sin ajuste)',
        XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            eval_metric='logloss', random_state=42, n_jobs=-1,
        ),
        X_train, y_train, X_test, y_test,
    ))

    df_resultados = pd.DataFrame(resultados)
    print()
    print(df_resultados.to_string(index=False))
    df_resultados.to_csv('resultado_experimento_boosting.csv', index=False)
    print('\nGuardado en DatasetEntrenamientoML/resultado_experimento_boosting.csv')


if __name__ == '__main__':
    main()
