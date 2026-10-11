"""
Paso 7: corrige un problema metodologico del paso 5/6 -- ahi se usaba el
ULTIMO estado financiero disponible de cada empresa, sin importar si ese
reporte era de ANTES o DESPUES de que la empresa entrara en insolvencia.
Usar datos de durante/despues de la crisis es "hacer trampa" (el modelo ve
la quiebra ya reflejada en el balance) o, al reves, quedarse sin señal si
la empresa dejo de reportar en cuanto entro en problemas.

Aqui:
  - Para las QUEBRADAS: se usa el ultimo estado financiero con fecha_corte
    en un año ESTRICTAMENTE ANTERIOR al año de apertura de su proceso de
    insolvencia (nits_anio_apertura.csv, extraido de la columna
    "AÑO_DE_APERTURA/CELEBRACION" de los Excel de Supersociedades).
  - Para las SANAS: no hay una "fecha de crisis" real, pero para evitar que
    el modelo aprenda "empresa antigua vs nueva" en vez de "sana vs
    quebrada", a cada sana se le asigna un año de referencia ALEATORIO
    tomado de la MISMA distribucion de años de apertura de las quebradas
    (semilla fija por NIT para reproducibilidad), y se usa su ultimo
    estado financiero anterior a ese año.

Esto es mas fiel a como se usaria el modelo en produccion: predecir la
quiebra usando SOLO informacion disponible antes de que ocurriera.
"""
import csv
import sys
import unicodedata

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

csv.field_size_limit(10_000_000)

ARCHIVOS = [
    ("financieros_raw/positivos_balance.csv", "financieros_raw/positivos_resultados.csv", 1),
    ("financieros_raw/negativos_balance.csv", "financieros_raw/negativos_resultados.csv", 0),
]
ANIO_APERTURA_CSV = "nits_anio_apertura.csv"
OUT_DATASET = "colombia_dataset_ratios_periodo_correcto.csv"

CUENTAS_BALANCE = {
    "activos corrientes totales": "Activo_Circulante",
    "pasivos corrientes totales": "Pasivo_Circulante",
    "inventarios corrientes": "Inventarios",
    "efectivo y equivalentes al efectivo": "Efectivo_Equivalentes",
    "total de activos": "Activo_Total",
    "total pasivos": "Pasivo_Total",
}
CUENTAS_UTILIDAD = {"ganancia (prdida)", "ganancia (perdida)"}

RATIOS_MODELO = [
    'razon_corriente', 'prueba_acida', 'endeudamiento_corto_plazo',
    'solvencia_general', 'cobertura_operacional', 'rentabilidad_activos',
    'capital_trabajo_sobre_activos',
]
REQUERIDOS = ['Activo_Circulante', 'Pasivo_Circulante', 'Activo_Total', 'Pasivo_Total']
TOPE_RATIO = 10.0
TASA_REAL = 0.032
N_REPETICIONES = 20


def normalizar(texto: str) -> str:
    if not texto:
        return ""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("�", "")
    return " ".join(t.lower().split())


def cargar_anios_apertura():
    d = {}
    with open(ANIO_APERTURA_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d[row["nit"]] = int(row["anio_apertura"])
    return d


def asignar_anio_referencia_negativos(nits_negativos, distribucion_anios):
    """A cada NIT sano le asigna, de forma determinista (semilla = hash del
    NIT), un año de referencia sacado de la distribucion real de años de
    apertura de las quebradas."""
    dist = np.array(distribucion_anios)
    resultado = {}
    for nit in nits_negativos:
        rng = np.random.default_rng(abs(hash(nit)) % (2**32))
        resultado[nit] = int(rng.choice(dist))
    return resultado


def es_periodo_valido_y_fecha(periodo: str, fecha_corte: str):
    """Devuelve el año efectivo del reporte (int) o None si es un periodo
    comparativo (Periodo Anterior) que no debe usarse como fecha propia."""
    p = normalizar(periodo)
    if p == "periodo anterior":
        return None
    try:
        return int((fecha_corte or "")[:4])
    except ValueError:
        return None


def leer_valores_con_corte(path, conceptos_objetivo, cortes, es_utilidad=False):
    """cortes: {nit: anio_limite} -- solo se acepta un reporte si su año
    es ESTRICTAMENTE MENOR a anio_limite[nit]. Se guarda, por NIT, el mas
    reciente que cumpla esa condicion."""
    por_nit = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, row in enumerate(csv.DictReader(f), 1):
            if n % 1_000_000 == 0:
                print(f"    {n:,} filas leidas de {path}")
                sys.stdout.flush()

            nit = row.get("nit")
            limite = cortes.get(nit)
            if limite is None:
                continue

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
            anio_reporte = es_periodo_valido_y_fecha(row.get("periodo"), fecha)
            if anio_reporte is None or anio_reporte >= limite:
                continue
            try:
                valor = float(row.get("valor"))
            except (TypeError, ValueError):
                continue

            actual = por_nit.get(nit)
            if actual is None or fecha > actual[0]:
                por_nit[nit] = (fecha, {campo: valor})
            elif fecha == actual[0]:
                actual[1][campo] = valor
    return por_nit


def calcular_ratios_liquidez(row: dict):
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
    anios_apertura = cargar_anios_apertura()
    dist_anios = list(anios_apertura.values())
    print(f"NIT con año de apertura conocido: {len(anios_apertura):,}")

    filas = []
    for path_balance, path_resultados, etiqueta in ARCHIVOS:
        clase = "POSITIVOS (quiebra)" if etiqueta == 1 else "NEGATIVOS (sanas)"
        print(f"\n=== {clase} ===")

        if etiqueta == 1:
            nits_de_este_archivo = set()
            with open(path_balance, encoding="utf-8", errors="replace") as f:
                for row in csv.DictReader(f):
                    nits_de_este_archivo.add(row["nit"])
            cortes = {n: anios_apertura[n] for n in nits_de_este_archivo if n in anios_apertura}
            print(f"  {len(nits_de_este_archivo):,} NIT en el archivo, "
                  f"{len(cortes):,} con año de apertura conocido (se usan solo esos)")
        else:
            nits_de_este_archivo = set()
            with open(path_balance, encoding="utf-8", errors="replace") as f:
                for row in csv.DictReader(f):
                    nits_de_este_archivo.add(row["nit"])
            cortes = asignar_anio_referencia_negativos(nits_de_este_archivo, dist_anios)
            print(f"  {len(nits_de_este_archivo):,} NIT, año de referencia asignado "
                  f"aleatoriamente de la distribucion de aperturas")

        print(f"  leyendo balance: {path_balance}")
        balance = leer_valores_con_corte(path_balance, CUENTAS_BALANCE, cortes)
        print(f"  NIT con balance anterior a su año de referencia: {len(balance):,}")

        print(f"  leyendo resultados: {path_resultados}")
        resultados = leer_valores_con_corte(path_resultados, {}, cortes, es_utilidad=True)
        print(f"  NIT con utilidad neta anterior a su año de referencia: {len(resultados):,}")

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
                'anio_referencia': cortes[nit],
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


def submuestrear_idx(y_arr, tasa, semilla):
    rng = np.random.default_rng(semilla)
    idx_neg = np.flatnonzero(y_arr == 0)
    idx_pos = np.flatnonzero(y_arr == 1)
    n_pos = int(round(tasa * len(idx_neg) / (1 - tasa)))
    n_pos = min(n_pos, len(idx_pos))
    return np.concatenate([idx_neg, rng.choice(idx_pos, n_pos, replace=False)])


def entrenar_escenario_c(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("ESCENARIO C (con periodo corregido) — entrena con todos los "
          "positivos, evalua a prevalencia real")
    print("=" * 70)

    X = df[RATIOS_MODELO].clip(-TOPE_RATIO, TOPE_RATIO).values
    y = df['quiebra'].values

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    X_train, X_resto, y_train, y_resto = train_test_split(
        X_escalado, y, test_size=0.4, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(
        X_resto, y_resto, test_size=0.5, random_state=42, stratify=y_resto)

    print(f"Train: {len(y_train):,} empresas, {int(y_train.sum()):,} quebradas "
          f"({y_train.mean()*100:.1f}%)")

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced',
        random_state=42, n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    proba_val = clf.predict_proba(X_val)[:, 1]
    umbrales = []
    for s in range(N_REPETICIONES):
        idx = submuestrear_idx(y_val, TASA_REAL, 1000 + s)
        u, _ = _mejor_umbral_f1(y_val[idx], proba_val[idx])
        umbrales.append(u)
    umbral = float(np.median(umbrales))
    print(f"Umbral calibrado en validacion a prevalencia real: {umbral:.2f}")

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

    print(f"\n--- METRICAS SOBRE TEST A PREVALENCIA REAL ({TASA_REAL*100:.1f}%) ---")
    for nombre, clave in (('F1-score', 'f1'), ('Precision', 'precision'),
                          ('Recall', 'recall'), ('Accuracy', 'accuracy'),
                          ('ROC-AUC', 'roc_auc'), ('PR-AUC', 'pr_auc')):
        vals = np.array(met[clave]) * 100
        print(f"  {nombre:10s} {vals.mean():5.1f}%  (+/- {vals.std():.1f})")

    print("\n--- IMPORTANCIA DE CADA RATIO ---")
    for ratio, imp in sorted(zip(RATIOS_MODELO, clf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {ratio:32s} {imp*100:5.1f}%")

    print("\nReferencia — Escenario C anterior (sin corregir periodo): F1 26.0%, PR-AUC 19.8%")
    print("Referencia — produccion actual (Taiwan): F1 46.8%, PR-AUC 43.3%")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    datos = construir_dataset()
    entrenar_escenario_c(datos)
