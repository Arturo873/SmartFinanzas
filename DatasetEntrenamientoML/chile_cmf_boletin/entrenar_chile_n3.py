"""
Intento de entrenamiento/validacion con datos chilenos reales (CMF x Boletin
Concursal) para el modelo de riesgo de insolvencia.

Contexto: el cruce por RUT entre CMF (estados financieros) y Boletin
Concursal (empresas en Liquidacion) dio solo 3 positivos reales
(ver cruce_viabilidad.py / resultado_interseccion.csv). Este script
existe UNICAMENTE para dejar documentado, con numeros reales, por que
n=3 no es entrenable ni validable con significancia estadistica -- no
para producir un modelo utilizable.

No modifica busqueda_mejora_f1.md ni el modelo de produccion
(AppWeb/modelo_oficial/). Solo genera evidencia cruda en esta carpeta.

Los 7 ratios se calculan EXACTAMENTE igual que
AppWeb/views.py -> calcular_ratios_liquidez(), a partir de las cuentas
IFRS de CMF (taxonomia ESF C/NC para balance, ERFG para resultado).
"""
import csv
import glob
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.preprocessing import MinMaxScaler

CMF_DIR = "cmf_raw"
INTERSECCION_CSV = "resultado_interseccion.csv"
OUT_DATASET = "chile_dataset_ratios.csv"

# Mapeo cuenta CMF -> campo usado por calcular_ratios_liquidez()
CUENTAS_BALANCE = {
    "Activos corrientes totales": "Activo_Circulante",
    "Pasivos corrientes totales": "Pasivo_Circulante",
    "Inventarios corrientes": "Inventarios",
    "Efectivo y equivalentes al efectivo": "Efectivo_Equivalentes",
    "Total de activos": "Activo_Total",
    "Total de pasivos": "Pasivo_Total",
}
TAXONOMIA_BALANCE = "ESF C/NC"
CUENTA_UTILIDAD = "Ganancia (pérdida)"
TAXONOMIA_UTILIDAD = "ERFG"


def normalizar_rut_base(rut: str) -> str:
    if not rut:
        return ""
    rut = str(rut).strip().upper().replace(".", "").replace(" ", "")
    rut = rut.split("-")[0]
    return rut.lstrip("0") or "0"


def cargar_positivos():
    positivos = set()
    with open(INTERSECCION_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            positivos.add(normalizar_rut_base(row["rut_normalizado"]))
    return positivos


def extraer_estados_financieros():
    """Para cada RUT, se queda con el ULTIMO periodo (mayor YYYYMM)
    que tenga registros, y guarda todas sus cuentas de ese periodo."""
    ultimo_periodo = {}   # rut -> periodo (int)
    cuentas_periodo = {}  # rut -> {cuenta: valor} del ultimo periodo visto

    archivos = sorted(glob.glob(f"{CMF_DIR}/eifrs_*.txt"))
    for path in archivos:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                campos = line.rstrip("\n").split(";")
                if len(campos) < 9:
                    continue
                periodo_s, rut_raw, razon, _flag, _moneda, cuenta, valor_s, _tax, tipo = campos[:9]
                try:
                    periodo = int(periodo_s)
                    valor = float(valor_s)
                except ValueError:
                    continue

                rut = normalizar_rut_base(rut_raw)
                if not rut:
                    continue

                es_cuenta_relevante = (
                    (tipo == TAXONOMIA_BALANCE and cuenta in CUENTAS_BALANCE)
                    or (tipo == TAXONOMIA_UTILIDAD and cuenta == CUENTA_UTILIDAD)
                )
                if not es_cuenta_relevante:
                    continue

                if rut not in ultimo_periodo or periodo > ultimo_periodo[rut]:
                    ultimo_periodo[rut] = periodo
                    cuentas_periodo[rut] = {"_razon_social": razon}

                if periodo == ultimo_periodo[rut]:
                    if tipo == TAXONOMIA_BALANCE:
                        cuentas_periodo[rut][CUENTAS_BALANCE[cuenta]] = valor
                    else:
                        cuentas_periodo[rut]["Utilidad_Neta"] = valor

    return ultimo_periodo, cuentas_periodo


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


RATIOS_MODELO = [
    'razon_corriente', 'prueba_acida', 'endeudamiento_corto_plazo',
    'solvencia_general', 'cobertura_operacional', 'rentabilidad_activos',
    'capital_trabajo_sobre_activos',
]
REQUERIDOS = ['Activo_Circulante', 'Pasivo_Circulante', 'Activo_Total', 'Pasivo_Total']


def construir_dataset():
    positivos = cargar_positivos()
    print(f"RUT positivos (quiebra real, del cruce): {len(positivos)}")

    ultimo_periodo, cuentas_periodo = extraer_estados_financieros()
    print(f"RUT con al menos alguna cuenta de balance/resultado: {len(cuentas_periodo)}")

    filas = []
    descartados_sin_balance = 0
    for rut, cuentas in cuentas_periodo.items():
        if not all(campo in cuentas for campo in REQUERIDOS):
            descartados_sin_balance += 1
            continue
        ratios = calcular_ratios_liquidez(cuentas)
        fila = {
            'rut': rut,
            'razon_social': cuentas.get('_razon_social', ''),
            'periodo': ultimo_periodo[rut],
            'quiebra': 1 if rut in positivos else 0,
        }
        fila.update(ratios)
        filas.append(fila)

    print(f"RUT descartados por no tener balance clasificado corriente/no corriente "
          f"(bancos, seguros, AFP, etc. con otra taxonomia): {descartados_sin_balance}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT_DATASET, index=False, encoding="utf-8")
    print(f"Dataset final: {len(df)} empresas, {df['quiebra'].sum()} positivas (quiebra=1)")
    print(f"Guardado en {OUT_DATASET}")
    return df


def intentar_entrenar(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("INTENTO DE ENTRENAMIENTO CON n=%d POSITIVOS" % df['quiebra'].sum())
    print("=" * 70)

    TOPE = 10.0
    X = df[RATIOS_MODELO].clip(-TOPE, TOPE).values
    y = df['quiebra'].values

    escalador = MinMaxScaler()
    X_escalado = escalador.fit_transform(X)

    n_pos = int(y.sum())
    if n_pos < 2:
        print("Menos de 2 positivos: ni siquiera se puede intentar un split "
              "train/test estratificado. Abortando.")
        return

    def correr_splits(stratify_arg, etiqueta):
        print(f"\n--- {etiqueta} ---")
        resultados = []
        for seed in range(10):
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_escalado, y, test_size=0.2, random_state=seed, stratify=stratify_arg
                )
            except ValueError as e:
                print(f"  seed={seed}: split imposible ({e})")
                continue

            clf = RandomForestClassifier(
                n_estimators=300, max_depth=8, class_weight='balanced',
                random_state=42, n_jobs=-1,
            )
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)

            f1 = f1_score(y_test, y_pred, zero_division=0)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            acc = accuracy_score(y_test, y_pred)
            n_pos_test = int(y_test.sum())

            resultados.append(f1)
            print(f"  seed={seed}: test set tiene {n_pos_test} positivo(s) de "
                  f"{len(y_test)} filas | F1={f1*100:.1f}%  precision={precision*100:.1f}%  "
                  f"recall={recall*100:.1f}%  accuracy={acc*100:.1f}%")

        if resultados:
            print(f"  F1 segun la semilla: min={min(resultados)*100:.1f}%  "
                  f"max={max(resultados)*100:.1f}%  "
                  f"rango={((max(resultados)-min(resultados))*100):.1f} puntos")
        return resultados

    print("\nProbando train_test_split(test_size=0.2) con distintas semillas, "
          "primero CON estratificacion (lo que haria un pipeline normal) y "
          "luego SIN estratificacion (split puramente aleatorio), para ver "
          "si el resultado depende de que caso puntual cae en el set de prueba:")

    res_estratificado = correr_splits(y, "CON stratify=y")
    res_aleatorio = correr_splits(None, "SIN stratify (random_state controla todo)")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    if res_estratificado and max(res_estratificado) == min(res_estratificado) == 0.0:
        print(
            "Con stratify=y, sklearn asigna SIEMPRE 1 de los 3 positivos al "
            "test set (redondeo determinista de 3*0.2=0.6 -> 1), sin importar "
            "la semilla. El modelo nunca predice ese unico positivo en "
            "ninguna de las 10 corridas: F1=0.0% siempre. No es que el "
            "modelo generalice mal a Chile -- es que 2 ejemplos de "
            "entrenamiento no alcanzan para que un RandomForest aprenda "
            "ningun patron de insolvencia, y 1 ejemplo de prueba no alcanza "
            "para medir nada con significancia estadistica."
        )
    if res_aleatorio:
        distintos_f1 = sorted(set(round(f * 100, 1) for f in res_aleatorio))
        if len(distintos_f1) == 1:
            print(
                f"\nSin estratificar, la CANTIDAD de positivos que cae en "
                f"test si varia con la semilla (0, 1, 2 o 3 de 3 casos, ver "
                f"arriba), pero el F1 resultante es {distintos_f1[0]}% en las "
                f"10 corridas: el modelo NUNCA identifica como riesgo alto "
                f"ninguna de las 3 quiebras reales chilenas, sin importar "
                f"que caso quede en el set de prueba ni cuantos positivos "
                f"vea en entrenamiento. Con solo 2-3 ejemplos de la clase "
                f"minoritaria, RandomForest no logra aprender un patron de "
                f"insolvencia generalizable -- confirma, con datos "
                f"empiricos y no solo con el argumento teorico, que n=3 no "
                f"es entrenable ni validable."
            )
        else:
            print(
                f"\nSin estratificar, el F1 SI cambia segun la semilla: "
                f"valores unicos observados = {distintos_f1}%. Confirma que "
                f"el numero reportado depende por completo de que caso cae "
                f"del lado del test, no de cuanto 'aprende' el modelo. "
                f"Ningun numero de esta tabla debe citarse como metrica de "
                f"rendimiento del modelo en Chile."
            )


if __name__ == "__main__":
    df = construir_dataset()
    intentar_entrenar(df)
