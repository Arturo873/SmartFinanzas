"""
Experimento: ¿combinar el dataset American Bankruptcy (Lombardo et al. 2022,
Kaggle "US Company Bankruptcy Prediction", 78,682 filas, 8,262 empresas
NYSE/NASDAQ 1999-2018, 6.63% quiebras) con Taiwan sube el F1?

Mapeo de columnas verificado empiricamente contra identidades contables
(GrossProfit = NetSales-COGS exacto; EBIT = EBITDA-D&A exacto; TotalAssets
>= CurrentAssets en 99.99% de filas) usando el orden oficial del paper:
  X1  = Current assets            X10 = Total assets
  X2  = Cost of goods sold        X11 = Total Long-term debt
  X3  = Depreciation/amortization X12 = EBIT
  X4  = EBITDA                    X13 = Gross Profit
  X5  = Inventory                 X14 = Total Current Liabilities
  X6  = Net Income                X15 = Retained Earnings
  X7  = Total Receivables         X16 = Total Revenue
  X8  = Market value              X17 = Total Liabilities
  X9  = Net sales                 X18 = Total Operating Expenses

Nota: el mirror en GitHub (sowide/bankruptcy_dataset) tiene las columnas
X1-X18 reordenadas respecto al paper original -- NO usar ese CSV para
mapear ratios, produce resultados sin sentido (Activo Total < Activo
Circulante en 72% de filas). Este script usa el CSV descargado directo de
Kaggle ("US Company Bankruptcy Prediction/american_bankruptcy.csv"), que
sí preserva el orden correcto.

Misma metodologia que experimento_combinar_polish.py: split de Taiwan
primero, dataset externo agregado solo al train, test set de Taiwan
intacto.

Uso:
    python DatasetEntrenamientoML/experimento_combinar_american.py
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
    TOPE_RATIO,
    cargar_y_mapear_dataset,
    _mejor_umbral_f1,
)

RUTA_AMERICAN = 'US Company Bankruptcy Prediction/american_bankruptcy.csv'


def cargar_american() -> pd.DataFrame:
    raw = pd.read_csv(RUTA_AMERICAN)

    ratios = pd.DataFrame(index=raw.index)
    ratios['razon_corriente'] = (raw['X1'] / raw['X14']).clip(upper=TOPE_RATIO)
    ratios['prueba_acida'] = ((raw['X1'] - raw['X5']) / raw['X14']).clip(upper=TOPE_RATIO)
    ratios['endeudamiento_corto_plazo'] = (raw['X14'] / raw['X17']).clip(upper=TOPE_RATIO)
    ratios['solvencia_general'] = (raw['X10'] / raw['X17']).clip(upper=TOPE_RATIO)
    ratios['cobertura_operacional'] = (raw['X6'] / raw['X14']).clip(-TOPE_RATIO, TOPE_RATIO)
    ratios['rentabilidad_activos'] = (raw['X6'] / raw['X10']).clip(-TOPE_RATIO, TOPE_RATIO)
    ratios['capital_trabajo_sobre_activos'] = ((raw['X1'] - raw['X14']) / raw['X10']).clip(-TOPE_RATIO, TOPE_RATIO)
    ratios['Bankrupt'] = (raw['status_label'] == 'failed').astype(int)

    antes = len(ratios)
    ratios = ratios.replace([np.inf, -np.inf], np.nan).dropna()
    print(f'American: {antes} filas crudas -> {len(ratios)} tras quitar inf/NaN')
    print(f'American: {int(ratios["Bankrupt"].sum())} quiebras de {len(ratios)} filas '
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

    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_taiwan, y_taiwan, test_size=0.2, random_state=42, stratify=y_taiwan
    )

    american = cargar_american()
    X_american = american[RATIOS_MODELO].values
    y_american = american['Bankrupt'].values

    escalador = MinMaxScaler()
    escalador.fit(np.vstack([X_train_t, X_american]))

    X_train_t_esc = escalador.transform(X_train_t)
    X_test_t_esc = escalador.transform(X_test_t)
    X_american_esc = escalador.transform(X_american)
    X_train_comb = np.vstack([X_train_t_esc, X_american_esc])
    y_train_comb = np.concatenate([y_train_t, y_american])

    resultados = []

    resultados.append(evaluar(
        'baseline: solo Taiwan',
        RandomForestClassifier(n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1),
        X_train_t_esc, y_train_t, X_test_t_esc, y_test_t,
    ))

    resultados.append(evaluar(
        'Taiwan train + American combinados',
        RandomForestClassifier(n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1),
        X_train_comb, y_train_comb, X_test_t_esc, y_test_t,
    ))

    rus = RandomUnderSampler(sampling_strategy=1.0, random_state=42)
    X_us, y_us = rus.fit_resample(X_train_comb, y_train_comb)
    resultados.append(evaluar(
        'Taiwan+American + undersampling 1:1',
        RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1),
        X_us, y_us, X_test_t_esc, y_test_t,
    ))

    smote = SMOTE(random_state=42)
    X_sm, y_sm = smote.fit_resample(X_train_comb, y_train_comb)
    resultados.append(evaluar(
        'Taiwan+American + SMOTE 1:1',
        RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1),
        X_sm, y_sm, X_test_t_esc, y_test_t,
    ))

    smoteenn = SMOTEENN(random_state=42)
    X_se, y_se = smoteenn.fit_resample(X_train_comb, y_train_comb)
    resultados.append(evaluar(
        'Taiwan+American + SMOTEENN',
        RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1),
        X_se, y_se, X_test_t_esc, y_test_t,
    ))

    # Solo American como dataset unico (train/test propios), para ver su F1 nativo
    X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(
        escalador.transform(X_american), y_american, test_size=0.2, random_state=42, stratify=y_american
    )
    resultados.append(evaluar(
        'solo American (train/test propios)',
        RandomForestClassifier(n_estimators=300, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1),
        X_train_a, y_train_a, X_test_a, y_test_a,
    ))

    df_resultados = pd.DataFrame(resultados)
    print()
    print(df_resultados.to_string(index=False))
    df_resultados.to_csv('resultado_experimento_american.csv', index=False)
    print('\nGuardado en DatasetEntrenamientoML/resultado_experimento_american.csv')


if __name__ == '__main__':
    main()
