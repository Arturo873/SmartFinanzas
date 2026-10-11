"""
Paso 3: arma una muestra de NIT "sanos" (NO en el listado de insolvencia)
que si tengan estados financieros NIIF, paginando el dataset de balance
(pfdp-zks5) y quedandonos con NIT unicos hasta juntar META_NEGATIVOS.

Excluye los 7477 NIT que aparecieron alguna vez en insolvencia (2019-2025),
no solo los 3429 con financieros, para evitar cualquier contaminacion.
"""
import csv
import json
import os
import socket
import sys
import time
import urllib.parse
import urllib.request

socket.setdefaulttimeout(50)  # backstop: fuerza timeout aunque urlopen no lo respete

NITS_INSOLVENCIA_CSV = "nits_insolvencia.csv"
OUT_CSV = "nits_negativos_muestra.csv"
RESOURCE_ID = "pfdp-zks5"
META_NEGATIVOS = 6000
PAGE_SIZE = 5000
MAX_PAGINAS = 1200
CHECKPOINT_CADA = 10  # paginas


def cargar_insolventes():
    with open(NITS_INSOLVENCIA_CSV, encoding="utf-8") as f:
        return {row["nit"] for row in csv.DictReader(f)}


def cargar_checkpoint():
    """Si ya existe un CSV parcial de una corrida anterior, retoma desde ahi."""
    if not os.path.exists(OUT_CSV):
        return set(), None
    with open(OUT_CSV, encoding="utf-8") as f:
        nits = sorted({row["nit"] for row in csv.DictReader(f)})
    if not nits:
        return set(), None
    print(f"Retomando checkpoint previo: {len(nits)} negativos ya guardados, "
          f"continuando desde nit={nits[-1]}")
    return set(nits), nits[-1]


def guardar_checkpoint(negativos):
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nit"])
        for n in sorted(negativos):
            w.writerow([n])


def consultar_pagina(last_nit):
    """Paginacion por keyset (nit > ultimo visto) en vez de $offset: en
    Socrata el offset se vuelve muy lento a medida que crece, mientras que
    un WHERE con $order sobre la columna ordenada se mantiene rapido."""
    params = {
        "$select": "nit",
        "$order": "nit",
        "$limit": PAGE_SIZE,
    }
    if last_nit is not None:
        params["$where"] = f"nit > '{last_nit}'"
    url = f"https://www.datos.gov.co/resource/{RESOURCE_ID}.json?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for intento in range(4):
        print(f"    solicitando pagina despues de nit={last_nit} (intento {intento+1})")
        sys.stdout.flush()
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.load(r)
                print(f"    respuesta en {time.time()-t0:.1f}s, {len(data)} filas")
                return data
        except Exception as e:
            print(f"    reintento last_nit={last_nit} ({e}) tras {time.time()-t0:.1f}s")
            time.sleep(2)
    return []


def main():
    insolventes = cargar_insolventes()
    print(f"NIT en insolvencia a excluir: {len(insolventes)}")

    negativos, last_nit = cargar_checkpoint()
    pagina = 0
    while len(negativos) < META_NEGATIVOS and pagina < MAX_PAGINAS:
        data = consultar_pagina(last_nit)
        if not data:
            print(f"  pagina vacia despues de {last_nit}, deteniendo")
            break
        nuevos = 0
        for row in data:
            nit = row.get("nit")
            if nit and nit not in insolventes and nit not in negativos:
                negativos.add(nit)
                nuevos += 1
        nuevo_last_nit = data[-1]["nit"]
        if nuevo_last_nit == last_nit:
            print(f"  nit={last_nit} tiene mas de {PAGE_SIZE} filas propias, deteniendo para evitar loop")
            break
        last_nit = nuevo_last_nit
        pagina += 1
        if pagina % CHECKPOINT_CADA == 0:
            guardar_checkpoint(negativos)
        if pagina % 20 == 0 or nuevos == 0:
            print(f"  pagina {pagina} (hasta nit={last_nit}): +{nuevos} nuevos, "
                  f"total negativos={len(negativos)}")

    print(f"\nTotal NIT negativos (sanos) recolectados: {len(negativos)}")
    guardar_checkpoint(negativos)
    print(f"Guardado en {OUT_CSV}")


if __name__ == "__main__":
    main()
