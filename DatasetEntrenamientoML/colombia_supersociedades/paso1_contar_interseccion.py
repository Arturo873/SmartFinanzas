"""
Paso 1 (rapido, liviano): para cada lote de NIT en insolvencia, consulta
solo los NIT DISTINCT que existen en el dataset de Estados Financieros NIIF
de datos.gov.co, para medir el tamano real de la interseccion ANTES de
descargar todas las filas (que puede ser mucho volumen).
"""
import csv
import time
import urllib.parse
import urllib.request
import json

NITS_CSV = "nits_insolvencia.csv"
API_BASE = "https://www.datos.gov.co/resource/pfdp-zks5.json"
LOTE = 40
OUT_CSV = "nits_con_financieros.csv"


def cargar_nits():
    nits = []
    with open(NITS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nits.append(row["nit"])
    return nits


def consultar_lote(lote):
    where = "nit in (" + ",".join(f"'{n}'" for n in lote) + ")"
    params = {"$select": "distinct nit", "$where": where, "$limit": 1000}
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:
            print(f"    reintento ({e})")
            time.sleep(2)
    return []


def main():
    nits = cargar_nits()
    print(f"Total NIT a verificar: {len(nits)}")

    encontrados = []
    for i in range(0, len(nits), LOTE):
        lote = nits[i:i + LOTE]
        data = consultar_lote(lote)
        for row in data:
            encontrados.append(row["nit"])
        print(f"  lote {i}-{i+len(lote)}: {len(data)} con estados financieros "
              f"(acumulado: {len(encontrados)})")

    print(f"\nTotal NIT con estados financieros NIIF publicados: {len(encontrados)} "
          f"de {len(nits)} en insolvencia")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nit"])
        for n in sorted(set(encontrados)):
            w.writerow([n])
    print(f"Guardado en {OUT_CSV}")


if __name__ == "__main__":
    main()
