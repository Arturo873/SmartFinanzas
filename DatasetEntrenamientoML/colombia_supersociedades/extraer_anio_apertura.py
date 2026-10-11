"""
Extrae, para cada NIT en insolvencia, el AÑO DE APERTURA/CELEBRACION del
proceso concursal (columna presente en los Excel crudos de
insolvencia_raw/, con nombre variable segun el año: 'A�O_DE_APERTURA...',
'ANO_DE_APERTURA...', etc). Si un NIT aparece en varios cortes con distintos
años (por error de captura o porque tuvo mas de un proceso), se usa el MAS
ANTIGUO -- es la fecha mas conservadora para no usar datos "demasiado
tarde" como si fueran de antes de la crisis.
"""
import csv
import glob
import os
import openpyxl

RAW_DIR = "insolvencia_raw"
OUT_CSV = "nits_anio_apertura.csv"


def normalizar_nit(nit) -> str:
    if nit is None:
        return ""
    s = str(nit).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return "".join(ch for ch in s if ch.isdigit())


def procesar_archivo(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb[wb.sheetnames[0]]
    filas = ws.iter_rows(values_only=True)
    header = next(filas)
    header_norm = [str(h).strip().upper() if h else "" for h in header]

    i_nit = header_norm.index("NIT") if "NIT" in header_norm else None
    i_anio = None
    for i, h in enumerate(header_norm):
        if h.startswith("A") and "APERTURA" in h:
            i_anio = i
            break
    if i_nit is None or i_anio is None:
        print(f"  AVISO: {path} sin columnas NIT/anio reconocibles "
              f"(header={header_norm}), se omite")
        return []

    resultados = []
    for fila in filas:
        if i_nit >= len(fila) or i_anio >= len(fila):
            continue
        nit = normalizar_nit(fila[i_nit])
        anio_raw = fila[i_anio]
        if not nit or anio_raw is None:
            continue
        try:
            anio = int(str(anio_raw)[:4])
        except ValueError:
            continue
        if 1990 < anio < 2027:
            resultados.append((nit, anio))
    return resultados


def main():
    anio_por_nit = {}
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.xlsx"))):
        filas = procesar_archivo(path)
        for nit, anio in filas:
            if nit not in anio_por_nit or anio < anio_por_nit[nit]:
                anio_por_nit[nit] = anio
        print(f"{os.path.basename(path)}: {len(filas)} filas con anio valido")

    print(f"\nNIT con anio de apertura identificado: {len(anio_por_nit)}")
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nit", "anio_apertura"])
        for nit, anio in sorted(anio_por_nit.items()):
            w.writerow([nit, anio])
    print(f"Guardado en {OUT_CSV}")


if __name__ == "__main__":
    main()
