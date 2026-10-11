"""
Paso 6: intenta mejorar el F1 del Escenario C (entrena con todos los
positivos, evalua a prevalencia real 3.2%) probando los algoritmos que
mejores resultados dieron en la busqueda sobre Taiwan
(ver busqueda_mejora_f1.md, Intento 9): EasyEnsembleClassifier y
BalancedRandomForestClassifier, comparados contra el RandomForest baseline.

Reutiliza colombia_dataset_ratios.csv (ya generado por el paso 5), no
vuelve a leer los CSV crudos.
"""
import sys

import numpy as np
import pandas as pd
from imblearn.ensemble import BalancedRandomForestClassifier, EasyEnsembleClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

DATASET_CSV = "colombia_dataset_ratios.csv"
RATIOS_MODELO = [
    'razon_corriente', 'prueba_acida', 'endeudamiento_corto_plazo',
    'solvencia_general', 'cobertura_operacional', 'rentabilidad_activos',
    'capital_trabajo_sobre_activos',
]
TOPE_RATIO = 10.0
TASA_REAL = 0.032
N_REPETICIONES = 20


def _mejor_umbral_f1(y_true, proba_positiva):
    mejor_umbral, mejor_f1 = 0.5, -1.0
    for umbral in np.arange(0.05, 0.96, 0.01):
        pred = (proba_positiva >= umbral).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > mejor_f1:
            mejor_f1, mejor_umbral = f1, float(umbral)
    return mejor_umbral, mejor_f1


def submuestrear_idx(y_arr, tasa, semilla):
    rng = np.random.default_rng(semilla)
    idx_neg = np.flatnonzero(y_arr == 0)
    idx_pos = np.flatnonzero(y_arr == 1)
    n_pos = int(round(tasa * len(idx_neg) / (1 - tasa)))
    n_pos = min(n_pos, len(idx_pos))
    return np.concatenate([idx_neg, rng.choice(idx_pos, n_pos, replace=False)])


def evaluar_modelo(nombre, clf, X_train, y_train, X_val, y_val, X_test, y_test):
    print(f"\n--- {nombre} ---")
    clf.fit(X_train, y_train)

    proba_val = clf.predict_proba(X_val)[:, 1]
    umbrales = []
    for s in range(N_REPETICIONES):
        idx = submuestrear_idx(y_val, TASA_REAL, 1000 + s)
        u, _ = _mejor_umbral_f1(y_val[idx], proba_val[idx])
        umbrales.append(u)
    umbral = float(np.median(umbrales))

    proba_test = clf.predict_proba(X_test)[:, 1]
    met = {k: [] for k in ('f1', 'precision', 'recall', 'accuracy', 'roc_auc', 'pr_auc')}
    for s in range(N_REPETICIONES):
        idx = submuestrear_idx(y_test, TASA_REAL, 2000 + s)
        yt, pt = y_test[idx], proba_test[idx]
        yp = (pt >= umbral).astype(int)
        met['f1'].append(f1_score(yt, yp, zero_division=0))
        met['precision'].append(precision_score(yt, yp, zero_division=0))
        met['recall'].append(recall_score(yt, yp, zero_division=0))
        met['accuracy'].append(accuracy_score(yt, yp))
        met['roc_auc'].append(roc_auc_score(yt, pt))
        met['pr_auc'].append(average_precision_score(yt, pt))

    resumen = {}
    print(f"  umbral calibrado: {umbral:.2f}")
    for nombre_m, clave in (('F1-score', 'f1'), ('Precision', 'precision'),
                            ('Recall', 'recall'), ('Accuracy', 'accuracy'),
                            ('ROC-AUC', 'roc_auc'), ('PR-AUC', 'pr_auc')):
        vals = np.array(met[clave]) * 100
        resumen[clave] = vals.mean()
        print(f"  {nombre_m:10s} {vals.mean():5.1f}%  (+/- {vals.std():.1f})")
    return resumen


def main():
    df = pd.read_csv(DATASET_CSV)
    X = df[RATIOS_MODELO].clip(-TOPE_RATIO, TOPE_RATIO).values
    y = df['quiebra'].values

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    X_train, X_resto, y_train, y_resto = train_test_split(
        X_escalado, y, test_size=0.4, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(
        X_resto, y_resto, test_size=0.5, random_state=42, stratify=y_resto)

    print(f"Train: {len(y_train):,} ({int(y_train.sum()):,} quebradas, "
          f"{y_train.mean()*100:.1f}%)")
    print(f"Comparando algoritmos, evaluados a prevalencia real ({TASA_REAL*100:.1f}%), "
          f"{N_REPETICIONES} repeticiones cada uno:")

    modelos = {
        "RandomForest class_weight=balanced (baseline, Escenario C)": RandomForestClassifier(
            n_estimators=300, max_depth=8, class_weight='balanced',
            random_state=42, n_jobs=-1),
        "BalancedRandomForestClassifier": BalancedRandomForestClassifier(
            n_estimators=300, max_depth=8, random_state=42, n_jobs=-1,
            sampling_strategy='auto', replacement=True, bootstrap=False),
        "EasyEnsembleClassifier": EasyEnsembleClassifier(
            n_estimators=30, random_state=42, n_jobs=-1),
    }

    resultados = {}
    for nombre, clf in modelos.items():
        resultados[nombre] = evaluar_modelo(nombre, clf, X_train, y_train,
                                            X_val, y_val, X_test, y_test)

    print("\n" + "=" * 70)
    print("RESUMEN COMPARATIVO (F1 a prevalencia real 3.2%)")
    print("=" * 70)
    for nombre, r in sorted(resultados.items(), key=lambda kv: -kv[1]['f1']):
        print(f"  {r['f1']:5.1f}%  F1  |  {r['pr_auc']:5.1f}%  PR-AUC  |  {nombre}")
    print("\n  46.8%  F1  |  43.3%  PR-AUC  |  Referencia: produccion actual (Taiwan)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
