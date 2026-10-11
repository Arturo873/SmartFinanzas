"""
Cruce de viabilidad: CMF Chile (estados financieros IFRS) x Boletin Concursal
(procedimientos de liquidacion de empresas), cruzados por RUT normalizado.

Objetivo: medir cuantas empresas con estados financieros completos (CMF)
terminaron en un procedimiento de Liquidacion (Boletin Concursal), como
evidencia de viabilidad de un dataset chileno real para el modelo predictivo.

No modifica ni documenta busqueda_mejora_f1.md -- solo genera evidencia cruda.
"""
import csv
import glob
import re

CMF_DIR = "cmf_raw"
BOLETIN_CSV = "boletin_concursal_raw.csv"
OUT_CSV = "resultado_interseccion.csv"


def normalizar_rut_base(rut: str) -> str:
    """Deja solo el numero base del RUT, sin puntos, espacios ni digito
    verificador. CMF entrega el RUT sin DV (ej. '60503000'); el Boletin
    Concursal lo entrega con DV separado por guion (ej. '13824595-0').
    Para poder cruzar ambas fuentes hay que comparar por el numero base."""
    if not rut:
        return ""
    rut = rut.strip().upper().replace(".", "").replace(" ", "")
    rut = rut.split("-")[0]
    return rut.lstrip("0") or "0"


def cargar_rut_cmf():
    """RUT unicos con estados financieros en CMF (2009-2024), con razon social."""
    ruts = {}
    archivos = sorted(glob.glob(f"{CMF_DIR}/eifrs_*.txt"))
    print(f"Archivos CMF encontrados: {len(archivos)}")
    for path in archivos:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                campos = line.rstrip("\n").split(";")
                if len(campos) < 3:
                    continue
                rut_raw, razon = campos[1], campos[2]
                rut_norm = normalizar_rut_base(rut_raw)
                if rut_norm and rut_norm not in ruts:
                    ruts[rut_norm] = razon
    return ruts


def cargar_rut_boletin_liquidacion():
    """RUT unicos de Empresa Deudora en algun tipo de Liquidacion."""
    ruts = {}
    with open(BOLETIN_CSV, encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_proc = header.index("Procedimiento Concursal")
        idx_deudor = header.index("Deudor")
        idx_rut = header.index("RUT")
        n = 0
        for row in reader:
            n += 1
            if len(row) <= max(idx_proc, idx_deudor, idx_rut):
                continue
            proc = row[idx_proc]
            if "Empresa Deudora" in proc and re.search("Liquidaci", proc):
                rut_norm = normalizar_rut_base(row[idx_rut])
                if rut_norm and rut_norm not in ruts:
                    ruts[rut_norm] = row[idx_deudor]
        print(f"Filas totales boletin: {n}")
    return ruts


def main():
    cmf_ruts = cargar_rut_cmf()
    print(f"RUT unicos CMF (2009-2024): {len(cmf_ruts)}")

    boletin_ruts = cargar_rut_boletin_liquidacion()
    print(f"RUT unicos Boletin Concursal (Empresa Deudora, Liquidacion): {len(boletin_ruts)}")

    interseccion = sorted(set(cmf_ruts) & set(boletin_ruts))
    print(f"Interseccion (positivos reales con estados financieros): {len(interseccion)}")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rut_normalizado", "razon_social_cmf", "deudor_boletin"])
        for rut in interseccion:
            w.writerow([rut, cmf_ruts.get(rut, ""), boletin_ruts.get(rut, "")])

    print(f"\nResultado guardado en {OUT_CSV}")
    print("\nEmpresas encontradas:")
    for rut in interseccion:
        print(f"  {rut} | CMF: {cmf_ruts.get(rut)} | Boletin: {boletin_ruts.get(rut)}")


if __name__ == "__main__":
    main()
