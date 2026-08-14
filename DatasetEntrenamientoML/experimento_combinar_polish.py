"""
Experimento: ¿combinar el dataset Polish Companies Bankruptcy (UCI #365) con
el Taiwanese (en produccion) sube el F1 respecto de usar solo Taiwan?

Metodologia (para no repetir el error de mezclar sin split correcto):
  1. Split train/test del Taiwan SOLO (mismo random_state=42 que el modelo
     oficial) -> el test set queda intacto, nunca se le agregan filas Polish.
  2. Las filas Polish (los 5 horizontes 1year..5year.arff) se mapean a los
     mismos 7 ratios via las formulas publicas de atributos del dataset
     (ver PLOSIH_ATTR_MAP abajo) y se agregan UNICAMENTE al train set.
  3. Se evalua sobre el test set de Taiwan original, para que el numero sea
     comparable directamente con el baseline (46.8% F1).

Definicion de atributos Polish (documentacion publica UCI #365):
  Attr1  = net profit / total assets
  Attr2  = total liabilities / total assets
  Attr3  = working capital / total assets
  Attr4  = current assets / short-term liabilities
  Attr17 = total assets / total liabilities
  Attr46 = (current assets - inventory) / short-term liabilities
  Attr51 = short-term liabilities / total assets

Uso:
    python DatasetEntrenamientoML/experimento_combinar_polish.py
"""
import glob
import numpy as np
import pandas as pd
from scipy.io import arff
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTEENN

from entrenar_modelo_oficial import (
    RATIOS_MODELO,
    TOPE_RATIO,
    cargar_y_mapear_dataset,
    _mejor_umbral_f1,
)


def cargar_polish() -> pd.DataFrame:
    """Carga los 5 horizontes del Polish dataset y los mapea a los 7 ratios."""
    frames = []
    for ruta in sorted(glob.glob('polish_raw/*.arff')):
        data, _meta = arff.loadarff(ruta)
        df = pd.DataFrame(data)
        df['class'] = df['class'].str.decode('utf-8').astype(int)
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)

    ratios = pd.DataFrame(index=raw.index)
    ratios['razon_corriente'] = raw['Attr4'].clip(upper=TOPE_RATIO)
    ratios['prueba_acida'] = raw['Attr46'].clip(upper=TOPE_RATIO)
    ratios['endeudamiento_corto_plazo'] = (raw['Attr51'] / raw['Attr2']).clip(upper=TOPE_RATIO)
    ratios['solvencia_general'] = raw['Attr17'].clip(upper=TOPE_RATIO)
    # cobertura_operacional = utilidad_neta / pasivo_circulante = Attr1 / Attr51
    ratios['cobertura_operacional'] = (raw['Attr1'] / raw['Attr51']).clip(-TOPE_RATIO, TOPE_RATIO)
    ratios['rentabilidad_activos'] = raw['Attr1'].clip(-TOPE_RATIO, TOPE_RATIO)
    ratios['capital_trabajo_sobre_activos'] = raw['Attr3'].clip(-TOPE_RATIO, TOPE_RATIO)
    ratios['Bankrupt'] = raw['class']

    antes = len(ratios)
    ratios = ratios.replace([np.inf, -np.inf], np.nan).dropna()
    print(f'Polish: {antes} filas crudas -> {len(ratios)} tras quitar inf/NaN '
          f'({antes - len(ratios)} descartadas por division por cero o datos faltantes)')
    print(f'Polish: {int(ratios["Bankrupt"].sum())} quiebras de {len(ratios)} filas '
          f'({100 * ratios["Bankrupt"].mean():.1f}%)')
    return ratios


def evaluar(nombre, clf, X_train, y_train, X_test, y_test):
    clf.fit(X_train, y_train)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(clf, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1)[:, 1]
    umbral_optimo, f1_cv = _mejor_umbral_f1(y_train, proba_cv)
    proba_test = clf.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral_optimo).astype(int)
    return {
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


def main():
    taiwan = cargar_y_mapear_dataset()
    X_taiwan = taiwan[RATIOS_MODELO].values
    y_taiwan = taiwan['Bankrupt'].values

    # Split ANTES de tocar Polish, para que el test set sea 100% Taiwan
    # original e intacto (mismo random_state que el modelo oficial).
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_taiwan, y_taiwan, test_size=0.2, random_state=42, stratify=y_taiwan
    )

    polish = cargar_polish()
    X_polish = polish[RATIOS_MODELO].values
    y_polish = polish['Bankrupt'].values

    # Escalador ajustado SOLO sobre train de Taiwan + Polish (nunca sobre test)
    escalador = MinMaxScaler()
    X_train_combinado_crudo = np.vstack([X_train_t, X_polish])
    escalador.fit(X_train_combinado_crudo)

    X_train_t_esc = escalador.transform(X_train_t)
    X_test_t_esc = escalador.transform(X_test_t)
    X_polish_esc = escalador.transform(X_polish)
    X_train_combinado_esc = np.vstack([X_train_t_esc, X_polish_esc])
    y_train_combinado = np.concatenate([y_train_t, y_polish])

    resultados = []

    clf_base = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1
    )
    resultados.append(evaluar(
        'baseline: solo Taiwan (produccion actual)',
        clf_base, X_train_t_esc, y_train_t, X_test_t_esc, y_test_t,
    ))

    clf_comb = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1
    )
    resultados.append(evaluar(
        'Taiwan train + Polish (todos los horizontes) combinados',
        clf_comb, X_train_combinado_esc, y_train_combinado, X_test_t_esc, y_test_t,
    ))

    # Balanceo aplicado sobre el train combinado (Taiwan train + Polish),
    # test set de Taiwan intacto, igual metodologia que experimento_balanceo.py
    rus = RandomUnderSampler(sampling_strategy=1.0, random_state=42)
    X_us, y_us = rus.fit_resample(X_train_combinado_esc, y_train_combinado)
    resultados.append(evaluar(
        'Taiwan+Polish combinado + undersampling 1:1',
        RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1),
        X_us, y_us, X_test_t_esc, y_test_t,
    ))

    smote = SMOTE(random_state=42)
    X_sm, y_sm = smote.fit_resample(X_train_combinado_esc, y_train_combinado)
    resultados.append(evaluar(
        'Taiwan+Polish combinado + SMOTE 1:1',
        RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1),
        X_sm, y_sm, X_test_t_esc, y_test_t,
    ))

    smoteenn = SMOTEENN(random_state=42)
    X_se, y_se = smoteenn.fit_resample(X_train_combinado_esc, y_train_combinado)
    resultados.append(evaluar(
        'Taiwan+Polish combinado + SMOTEENN',
        RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1),
        X_se, y_se, X_test_t_esc, y_test_t,
    ))

    df_resultados = pd.DataFrame(resultados)
    print()
    print(df_resultados.to_string(index=False))
    df_resultados.to_csv('resultado_experimento_polish.csv', index=False)
    print('\nGuardado en DatasetEntrenamientoML/resultado_experimento_polish.csv')


if __name__ == '__main__':
    main()
