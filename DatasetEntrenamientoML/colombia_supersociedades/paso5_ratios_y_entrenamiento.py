"""
Paso 5: calcula los 7 ratios financieros y entrena/evalua el modelo con los
datos colombianos (Superintendencia de Sociedades via datos.gov.co).

Los 7 ratios se calculan EXACTAMENTE con la misma formula que
AppWeb/views.py -> calcular_ratios_liquidez(), para que el modelo entrenado
aqui sea directamente comparable (y reemplazable) con el de produccion
entrenado sobre Taiwan (DatasetEntrenamientoML/entrenar_modelo_oficial.py).

Etiqueta:
  quiebra = 1  -> empresa que aparecio en algun corte del listado de
                  insolvencia de Supersociedades 2019-2025 (reorganizacion
                  o liquidacion judicial).
  quiebra = 0  -> empresa con estados financieros NIIF que NUNCA aparecio
                  en esos listados.

Para cada empresa se usa el ULTIMO estado financiero disponible
(mayor fecha_corte), tomando solo los valores del periodo actual de ese
reporte (no los comparativos del periodo anterior).
"""
import csv
import sys
import unicodedata

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.preprocessing import MinMaxScaler

csv.field_size_limit(10_000_000)

ARCHIVOS = [
    ("financieros_raw/positivos_balance.csv", "financieros_raw/positivos_resultados.csv", 1),
    ("financieros_raw/negativos_balance.csv", "financieros_raw/negativos_resultados.csv", 0),
]
OUT_DATASET = "colombia_dataset_ratios.csv"

# Mapeo cuenta NIIF (Colombia) -> campo de calcular_ratios_liquidez()
CUENTAS_BALANCE = {
    "activos corrientes totales": "Activo_Circulante",
    "pasivos corrientes totales": "Pasivo_Circulante",
    "inventarios corrientes": "Inventarios",
    "efectivo y equivalentes al efectivo": "Efectivo_Equivalentes",
    "total de activos": "Activo_Total",
    "total pasivos": "Pasivo_Total",
}
# OJO: la fuente entrega los acentos corruptos ("Ganancia (p<?>rdida)"), y
# normalizar() elimina ese caracter, por lo que la cuenta queda literalmente
# como "ganancia (prdida)". Se aceptan ambas formas por si la fuente corrige
# la codificacion mas adelante.
CUENTAS_UTILIDAD = {"ganancia (prdida)", "ganancia (perdida)"}

RATIOS_MODELO = [
    'razon_corriente',
    'prueba_acida',
    'endeudamiento_corto_plazo',
    'solvencia_general',
    'cobertura_operacional',
    'rentabilidad_activos',
    'capital_trabajo_sobre_activos',
]
REQUERIDOS = ['Activo_Circulante', 'Pasivo_Circulante', 'Activo_Total', 'Pasivo_Total']
TOPE_RATIO = 10.0


def normalizar(texto: str) -> str:
    """Minusculas y sin tildes/caracteres corruptos, para poder comparar los
    nombres de cuenta pese a que la fuente entrega algunos mal codificados."""
    if not texto:
        return ""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("�", "")
    return " ".join(t.lower().split())


def es_periodo_actual(periodo: str, fecha_corte: str) -> bool:
    """Acepta el valor del periodo corriente del reporte y descarta el
    comparativo del periodo anterior."""
    p = normalizar(periodo)
    if p == "periodo actual":
        return True
    if p == "periodo anterior":
        return False
    anio = (fecha_corte or "")[:4]
    return bool(anio) and p.startswith(anio)


def leer_valores(path, conceptos_objetivo, es_utilidad=False):
    """Devuelve {nit: (fecha_corte, {campo: valor})} con el ultimo reporte."""
    por_nit = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, row in enumerate(csv.DictReader(f), 1):
            if n % 1_000_000 == 0:
                print(f"    {n:,} filas leidas de {path}")
                sys.stdout.flush()

            concepto = normalizar(row.get("concepto"))
            if es_utilidad:
                if concepto not in CUENTAS_UTILIDAD:
                    continue
                campo = "Utilidad_Neta"
            else:
                campo = conceptos_objetivo.get(concepto)
                if campo is None:
                    continue

            fecha = row.get("fecha_corte") or ""
            if not es_periodo_actual(row.get("periodo"), fecha):
                continue
            try:
                valor = float(row.get("valor"))
            except (TypeError, ValueError):
                continue

            nit = row.get("nit")
            actual = por_nit.get(nit)
            if actual is None or fecha > actual[0]:
                por_nit[nit] = (fecha, {campo: valor})
            elif fecha == actual[0]:
                actual[1][campo] = valor
    return por_nit


def calcular_ratios_liquidez(row: dict):
    """Copia exacta de AppWeb/views.py -> calcular_ratios_liquidez()."""
    activo_circulante = row.get('Activo_Circulante', 0)
    pasivo_circulante = row.get('Pasivo_Circulante', 0)
    inventario = row.get('Inventarios', 0)
    flujo_caja_operativo = row.get('Utilidad_Neta', 0)
    pasivo_total = row.get('Pasivo_Total', 0)
    activo_total = row.get('Activo_Total', 0)

    eps = 1e-6
    denom = pasivo_circulante if pasivo_circulante > 0 else eps
    denom_activo = activo_total if activo_total > 0 else eps

    return {
        'razon_corriente': activo_circulante / denom,
        'prueba_acida': (activo_circulante - inventario) / denom,
        'endeudamiento_corto_plazo': pasivo_circulante / (pasivo_total if pasivo_total > 0 else eps),
        'solvencia_general': activo_total / (pasivo_total if pasivo_total > 0 else eps),
        'cobertura_operacional': flujo_caja_operativo / denom,
        'rentabilidad_activos': flujo_caja_operativo / denom_activo,
        'capital_trabajo_sobre_activos': (activo_circulante - pasivo_circulante) / denom_activo,
    }


def construir_dataset():
    filas = []
    for path_balance, path_resultados, etiqueta in ARCHIVOS:
        clase = "POSITIVOS (quiebra)" if etiqueta == 1 else "NEGATIVOS (sanas)"
        print(f"\n=== {clase} ===")
        print(f"  leyendo balance: {path_balance}")
        balance = leer_valores(path_balance, CUENTAS_BALANCE)
        print(f"  NIT con datos de balance: {len(balance):,}")

        print(f"  leyendo resultados: {path_resultados}")
        resultados = leer_valores(path_resultados, {}, es_utilidad=True)
        print(f"  NIT con utilidad neta: {len(resultados):,}")

        completos, incompletos = 0, 0
        for nit, (fecha, cuentas) in balance.items():
            if not all(c in cuentas for c in REQUERIDOS):
                incompletos += 1
                continue
            datos = dict(cuentas)
            if nit in resultados:
                datos.update(resultados[nit][1])
            fila = {
                'nit': nit,
                'fecha_corte': fecha[:10],
                'quiebra': etiqueta,
            }
            fila.update(calcular_ratios_liquidez(datos))
            filas.append(fila)
            completos += 1
        print(f"  usables: {completos:,} | descartados por balance incompleto: {incompletos:,}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT_DATASET, index=False, encoding="utf-8")
    print(f"\nDataset final: {len(df):,} empresas "
          f"({int(df['quiebra'].sum()):,} quebradas / "
          f"{int((1 - df['quiebra']).sum()):,} sanas)")
    print(f"Guardado en {OUT_DATASET}")
    return df


def _mejor_umbral_f1(y_true, proba_positiva):
    mejor_umbral, mejor_f1 = 0.5, -1.0
    for umbral in np.arange(0.05, 0.96, 0.01):
        pred = (proba_positiva >= umbral).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > mejor_f1:
            mejor_f1, mejor_umbral = f1, float(umbral)
    return mejor_umbral, mejor_f1


def entrenar(df: pd.DataFrame, titulo: str):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)

    X = df[RATIOS_MODELO].clip(-TOPE_RATIO, TOPE_RATIO).values
    y = df['quiebra'].values
    print(f"Empresas: {len(y):,} | quebradas: {int(y.sum()):,} "
          f"({y.mean()*100:.1f}% de la muestra)")

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_escalado, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {len(y_train):,} ({int(y_train.sum()):,} quebradas) | "
          f"Test: {len(y_test):,} ({int(y_test.sum()):,} quebradas)")

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced',
        random_state=42, n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # Umbral optimo buscado por validacion cruzada SOLO en train (el test
    # nunca se toca para ajustar nada).
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba_cv = cross_val_predict(clf, X_train, y_train, cv=cv,
                                 method='predict_proba', n_jobs=-1)[:, 1]
    umbral, f1_cv = _mejor_umbral_f1(y_train, proba_cv)

    proba_test = clf.predict_proba(X_test)[:, 1]
    y_pred = (proba_test >= umbral).astype(int)

    print(f"\nUmbral optimo (CV sobre train): {umbral:.2f}  "
          f"(F1 en CV: {f1_cv*100:.1f}%)")
    print("\n--- METRICAS SOBRE EL TEST SET (20%, nunca visto) ---")
    print(f"  F1-score:  {f1_score(y_test, y_pred, zero_division=0)*100:.1f}%")
    print(f"  Precision: {precision_score(y_test, y_pred, zero_division=0)*100:.1f}%")
    print(f"  Recall:    {recall_score(y_test, y_pred, zero_division=0)*100:.1f}%")
    print(f"  Accuracy:  {accuracy_score(y_test, y_pred)*100:.1f}%")
    print(f"  ROC-AUC:   {roc_auc_score(y_test, proba_test)*100:.1f}%")
    print(f"  PR-AUC:    {average_precision_score(y_test, proba_test)*100:.1f}%")

    print("\n--- IMPORTANCIA DE CADA RATIO ---")
    for ratio, imp in sorted(zip(RATIOS_MODELO, clf.feature_importances_),
                             key=lambda x: -x[1]):
        print(f"  {ratio:32s} {imp*100:5.1f}%")


def entrenar_escenario_c(df: pd.DataFrame, tasa_real=0.032, n_repeticiones=20):
    """ESCENARIO C: entrena con TODOS los positivos disponibles (que es lo
    que se haria en produccion) pero calibra el umbral y evalua sobre
    conjuntos con la prevalencia real de quiebra (~3.2%).

    Separa dos cosas que los escenarios A y B mezclan:
      - cuanta senal hay para aprender  -> se usa todo el train
      - que tan dificil es el problema real -> val/test con prevalencia real

    Como a esa prevalencia el test queda con pocos positivos, la evaluacion
    se repite con `n_repeticiones` submuestreos distintos y se reporta
    promedio y desviacion, en vez de un unico numero ruidoso.
    """
    print("\n" + "=" * 70)
    print("ESCENARIO C — entrena con todos los positivos, evalua a prevalencia real")
    print("=" * 70)

    X = df[RATIOS_MODELO].clip(-TOPE_RATIO, TOPE_RATIO).values
    y = df['quiebra'].values

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    # 60% train / 20% validacion (calibrar umbral) / 20% test (reportar)
    X_train, X_resto, y_train, y_resto = train_test_split(
        X_escalado, y, test_size=0.4, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(
        X_resto, y_resto, test_size=0.5, random_state=42, stratify=y_resto)

    print(f"Train (senal completa): {len(y_train):,} empresas, "
          f"{int(y_train.sum()):,} quebradas ({y_train.mean()*100:.1f}%)")

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced',
        random_state=42, n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    def submuestrear_idx(y_arr, tasa, semilla):
        rng = np.random.default_rng(semilla)
        idx_neg = np.flatnonzero(y_arr == 0)
        idx_pos = np.flatnonzero(y_arr == 1)
        n_pos = int(round(tasa * len(idx_neg) / (1 - tasa)))
        n_pos = min(n_pos, len(idx_pos))
        return np.concatenate([idx_neg, rng.choice(idx_pos, n_pos, replace=False)])

    # Umbral calibrado sobre validacion a prevalencia real (nunca sobre test)
    proba_val = clf.predict_proba(X_val)[:, 1]
    umbrales = []
    for s in range(n_repeticiones):
        idx = submuestrear_idx(y_val, tasa_real, 1000 + s)
        u, _ = _mejor_umbral_f1(y_val[idx], proba_val[idx])
        umbrales.append(u)
    umbral = float(np.median(umbrales))
    print(f"Umbral calibrado en validacion a prevalencia real: {umbral:.2f}")

    proba_test = clf.predict_proba(X_test)[:, 1]
    met = {k: [] for k in ('f1', 'precision', 'recall', 'accuracy', 'roc_auc', 'pr_auc')}
    for s in range(n_repeticiones):
        idx = submuestrear_idx(y_test, tasa_real, 2000 + s)
        yt, pt = y_test[idx], proba_test[idx]
        yp = (pt >= umbral).astype(int)
        met['f1'].append(f1_score(yt, yp, zero_division=0))
        met['precision'].append(precision_score(yt, yp, zero_division=0))
        met['recall'].append(recall_score(yt, yp, zero_division=0))
        met['accuracy'].append(accuracy_score(yt, yp))
        met['roc_auc'].append(roc_auc_score(yt, pt))
        met['pr_auc'].append(average_precision_score(yt, pt))

    n_pos_test = int(round(tasa_real * (y_test == 0).sum() / (1 - tasa_real)))
    print(f"\n--- METRICAS SOBRE TEST A PREVALENCIA REAL ({tasa_real*100:.1f}%) ---")
    print(f"    ({(y_test == 0).sum():,} sanas + ~{n_pos_test} quebradas por repeticion, "
          f"{n_repeticiones} repeticiones)")
    for nombre, clave in (('F1-score', 'f1'), ('Precision', 'precision'),
                          ('Recall', 'recall'), ('Accuracy', 'accuracy'),
                          ('ROC-AUC', 'roc_auc'), ('PR-AUC', 'pr_auc')):
        vals = np.array(met[clave]) * 100
        print(f"  {nombre:10s} {vals.mean():5.1f}%  (+/- {vals.std():.1f})")


def submuestrear_a_tasa(df: pd.DataFrame, tasa_objetivo: float, semilla=42):
    """Deja todas las empresas sanas y submuestrea las quebradas para que
    representen `tasa_objetivo` del total, imitando la prevalencia real de
    quiebras (y la del dataset de Taiwan, 3.2%), que es la unica forma de
    comparar F1 de manera justa entre ambos datasets."""
    sanas = df[df['quiebra'] == 0]
    quebradas = df[df['quiebra'] == 1]
    n_quebradas = int(round(tasa_objetivo * len(sanas) / (1 - tasa_objetivo)))
    n_quebradas = min(n_quebradas, len(quebradas))
    muestra = pd.concat([sanas, quebradas.sample(n=n_quebradas, random_state=semilla)])
    return muestra.sample(frac=1, random_state=semilla).reset_index(drop=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    datos = construir_dataset()

    entrenar(datos, "ESCENARIO A — muestra tal como se descargo "
                    "(quiebras sobrerrepresentadas)")

    datos_realista = submuestrear_a_tasa(datos, 0.032)
    entrenar(datos_realista, "ESCENARIO B — prevalencia de quiebra realista (3.2%), "
                             "comparable 1:1 con el dataset de Taiwan")

    entrenar_escenario_c(datos)

    print("\n" + "=" * 70)
    print("REFERENCIA: modelo actual en produccion, entrenado con Taiwan")
    print("  (prevalencia de quiebra 3.2%): F1 46.8% | precision 36.2% | "
          "recall 65.9% | PR-AUC 43.3%")
    print("El ESCENARIO B es el unico comparable directamente con esa linea "
          "base;\nel ESCENARIO A infla el F1 por tener 36% de quiebras en vez "
          "de ~3%.")
    print("=" * 70)
