"""
Extrae el listado de NIT unicos en procesos de insolvencia (reorganizacion o
liquidacion) a partir de los cortes anuales de "Base Soporte Insolvencia" de
la Superintendencia de Sociedades de Colombia (descargados en insolvencia_raw/).

Salida: nits_insolvencia.csv (nit, nombre, proceso, anio_corte)
"""
import csv
import glob
import os
import openpyxl

RAW_DIR = "insolvencia_raw"
OUT_CSV = "nits_insolvencia.csv"


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

    def idx(*nombres):
        for n in nombres:
            if n in header_norm:
                return header_norm.index(n)
        return None

    i_nit = idx("NIT")
    i_nombre = idx("NOMBRE")
    i_proceso = idx("PROCESO")
    if i_nit is None:
        print(f"  AVISO: {path} no tiene columna NIT reconocible, se omite")
        return []

    resultados = []
    for fila in filas:
        if i_nit >= len(fila):
            continue
        nit = normalizar_nit(fila[i_nit])
        if not nit:
            continue
        nombre = fila[i_nombre] if i_nombre is not None and i_nombre < len(fila) else ""
        proceso = fila[i_proceso] if i_proceso is not None and i_proceso < len(fila) else ""
        resultados.append((nit, nombre, proceso))
    return resultados


def main():
    nits = {}
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.xlsx"))):
        filas = procesar_archivo(path)
        anio = os.path.basename(path)
        for nit, nombre, proceso in filas:
            if nit not in nits:
                nits[nit] = {"nombre": nombre, "proceso": proceso, "primer_corte": anio}
        print(f"{os.path.basename(path)}: {len(filas)} filas")

    print(f"\nNIT unicos en insolvencia (2019-2025, uniendo 7 cortes): {len(nits)}")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nit", "nombre", "proceso", "primer_corte_visto"])
        for nit, info in sorted(nits.items()):
            w.writerow([nit, info["nombre"], info["proceso"], info["primer_corte"]])

    print(f"Guardado en {OUT_CSV}")


if __name__ == "__main__":
    main()
