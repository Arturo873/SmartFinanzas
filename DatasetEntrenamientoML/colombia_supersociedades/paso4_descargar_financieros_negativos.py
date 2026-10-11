"""
Paso 4: descarga los estados financieros (balance = pfdp-zks5, resultados =
prwj-nzxa) de datos.gov.co para los NIT "sanos" (nits_negativos_muestra.csv,
salida del paso 3). Mismo patron que paso2 pero para la clase negativa.
"""
import csv
import json
import os
import socket
import sys
import time
import urllib.parse
import urllib.request

socket.setdefaulttimeout(50)

NITS_CSV = "nits_negativos_muestra.csv"
DATASETS = {
    "balance": "pfdp-zks5",
    "resultados": "prwj-nzxa",
}
LOTE = 20
OUT_PREFIX = "financieros_raw/negativos"


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
            sys.stdout.flush()
            time.sleep(2)
    return []


def nits_ya_procesados(out_path):
    """Si el CSV de salida ya existe (corrida previa interrumpida), junta
    los NIT que ya aparecen ahi para no volver a pedirlos."""
    if not os.path.exists(out_path):
        return set()
    with open(out_path, encoding="utf-8") as f:
        return {row["nit"] for row in csv.DictReader(f)}


def main():
    nits = cargar_nits()
    print(f"Total NIT a descargar: {len(nits)}")

    for nombre, resource_id in DATASETS.items():
        print(f"\n=== Descargando {nombre} ({resource_id}) ===")
        out_path = f"{OUT_PREFIX}_{nombre}.csv"
        procesados = nits_ya_procesados(out_path)
        pendientes = [n for n in nits if n not in procesados]
        print(f"  ya procesados antes: {len(procesados)} NIT distintos en el archivo, "
              f"pendientes: {len(pendientes)}")

        modo = "a" if procesados else "w"
        total_filas = 0
        with open(out_path, modo, newline="", encoding="utf-8") as f:
            w = None
            escribir_header = (modo == "w")
            for i in range(0, len(pendientes), LOTE):
                lote = pendientes[i:i + LOTE]
                data = consultar_lote(resource_id, lote)
                if data:
                    if w is None:
                        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                        if escribir_header:
                            w.writeheader()
                    for row in data:
                        w.writerow(row)
                    total_filas += len(data)
                    f.flush()
                if (i // LOTE) % 20 == 0:
                    print(f"  {i}/{len(pendientes)} NIT pendientes procesados, "
                          f"{total_filas} filas nuevas acumuladas")
                    sys.stdout.flush()
        print(f"{nombre}: {total_filas} filas nuevas -> {out_path}")


if __name__ == "__main__":
    main()
