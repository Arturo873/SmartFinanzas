"""
Paso 2: descarga TODAS las filas del dataset de Estados Financieros NIIF
(balance = pfdp-zks5, resultados = prwj-nzxa) de datos.gov.co para los
NIT que SI tienen estados financieros y estan en insolvencia
(nits_con_financieros.csv, salida del paso 1).

Guarda todo en bruto para procesar despues (calculo de ratios).
"""
import csv
import json
import time
import urllib.parse
import urllib.request

NITS_CSV = "nits_con_financieros.csv"
DATASETS = {
    "balance": "pfdp-zks5",
    "resultados": "prwj-nzxa",
}
LOTE = 20
OUT_PREFIX = "financieros_raw/positivos"


def cargar_nits():
    with open(NITS_CSV, encoding="utf-8") as f:
        return [row["nit"] for row in csv.DictReader(f)]


def consultar_lote(resource_id, lote):
    where = "nit in (" + ",".join(f"'{n}'" for n in lote) + ")"
    params = {"$where": where, "$limit": 50000}
    url = f"https://www.datos.gov.co/resource/{resource_id}.json?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            print(f"    reintento ({e})")
            time.sleep(2)
    return []


def main():
    nits = cargar_nits()
    print(f"Total NIT a descargar: {len(nits)}")

    for nombre, resource_id in DATASETS.items():
        print(f"\n=== Descargando {nombre} ({resource_id}) ===")
        out_path = f"{OUT_PREFIX}_{nombre}.csv"
        total_filas = 0
        primero = True
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = None
            for i in range(0, len(nits), LOTE):
                lote = nits[i:i + LOTE]
                data = consultar_lote(resource_id, lote)
                if data:
                    if primero:
                        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                        w.writeheader()
                        primero = False
                    for row in data:
                        w.writerow(row)
                    total_filas += len(data)
                if (i // LOTE) % 20 == 0:
                    print(f"  {i}/{len(nits)} NIT procesados, {total_filas} filas acumuladas")
        print(f"{nombre}: {total_filas} filas totales -> {out_path}")


if __name__ == "__main__":
    main()
