"""
Experimento: ¿balancear el train set (undersampling / SMOTE / SMOTEENN)
acerca el F1 al 80% exigido por RNF-08?

Mismo split train/test (80/20, stratify, random_state=42) que
entrenar_modelo_oficial.py, para que la comparacion sea justa. El
balanceo se aplica UNICAMENTE al train set; el test set se deja intacto
con la distribucion original (3.2% quiebras) para que el F1 medido sea
representativo del caso real, sin data leakage.

Resultados se agregan como "Intento 5" en busqueda_mejora_f1.md.

Uso:
    python DatasetEntrenamientoML/experimento_balanceo.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTEENN

from entrenar_modelo_oficial import (
    RATIOS_MODELO,
    cargar_y_mapear_dataset,
    _mejor_umbral_f1,
)


def evaluar(nombre, X_train, y_train, X_test, y_test):
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(
        clf, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1
    )[:, 1]
    umbral_optimo, f1_cv = _mejor_umbral_f1(y_train, proba_cv)

    proba_test = clf.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral_optimo).astype(int)

    resultado = {
        'experimento': nombre,
        'filas_train': len(y_train),
        'quiebras_train': int(y_train.sum()),
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 1),
        'precision': round(precision_score(y_test, y_pred, zero_division=0) * 100, 1),
        'recall': round(recall_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_test': round(f1_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_cv_train': round(f1_cv * 100, 1),
        'umbral': round(umbral_optimo, 2),
    }
    return resultado


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

    # Baseline: sin balanceo, class_weight='balanced' (equivale al modelo oficial actual)
    clf_base = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1
    )
    clf_base.fit(X_train, y_train)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(clf_base, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1)[:, 1]
    umbral_optimo, f1_cv = _mejor_umbral_f1(y_train, proba_cv)
    proba_test = clf_base.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral_optimo).astype(int)
    resultados.append({
        'experimento': 'baseline (class_weight=balanced, produccion actual)',
        'filas_train': len(y_train),
        'quiebras_train': int(y_train.sum()),
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 1),
        'precision': round(precision_score(y_test, y_pred, zero_division=0) * 100, 1),
        'recall': round(recall_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_test': round(f1_score(y_test, y_pred, zero_division=0) * 100, 1),
        'f1_cv_train': round(f1_cv * 100, 1),
        'umbral': round(umbral_optimo, 2),
    })

    # Experimento A: undersampling agresivo 1:1 (220 / 220, como sugirio ChatGPT)
    rus_1a1 = RandomUnderSampler(sampling_strategy=1.0, random_state=42)
    X_a, y_a = rus_1a1.fit_resample(X_train, y_train)
    resultados.append(evaluar('undersampling 1:1 (220/220)', X_a, y_a, X_test, y_test))

    # Experimento B: undersampling moderado 1:4 (220 / ~880) para no perder tanta señal
    rus_1a4 = RandomUnderSampler(sampling_strategy=0.25, random_state=42)
    X_b, y_b = rus_1a4.fit_resample(X_train, y_train)
    resultados.append(evaluar('undersampling 1:4 (220/~880)', X_b, y_b, X_test, y_test))

    # Experimento C: SMOTE puro hasta 1:1
    smote = SMOTE(random_state=42)
    X_c, y_c = smote.fit_resample(X_train, y_train)
    resultados.append(evaluar('SMOTE 1:1', X_c, y_c, X_test, y_test))

    # Experimento D: SMOTEENN (SMOTE + limpieza por Edited Nearest Neighbours)
    smoteenn = SMOTEENN(random_state=42)
    X_d, y_d = smoteenn.fit_resample(X_train, y_train)
    resultados.append(evaluar('SMOTEENN', X_d, y_d, X_test, y_test))

    df_resultados = pd.DataFrame(resultados)
    print(df_resultados.to_string(index=False))
    df_resultados.to_csv('resultado_experimento_balanceo.csv', index=False)
    print('\nGuardado en DatasetEntrenamientoML/resultado_experimento_balanceo.csv')


if __name__ == '__main__':
    main()
