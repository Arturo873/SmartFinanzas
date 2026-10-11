"""Paso 1: empresas chilenas reales (CMF, IFRS 2009-2024) con las 8 variables.

Lee los estados financieros crudos de la CMF (solo locales, no están en git:
DatasetEntrenamientoML/chile_cmf_boletin/cmf_raw/) y, por cada empresa y año,
toma el balance a diciembre (flujos de 12 meses). Calcula V1-V6 y el Z''EM de
Altman con AppWeb/variables_modelo.py (las mismas fórmulas que usa el sistema)
y V8 con el dato macro real del cuarto trimestre de ese año.

Etiqueta (insolvente = 1), según fuentes de documentacion/fuentes_modelo_ml.md:
  - Z''EM de Altman < 1,10 (Altman et al., 2017; Riquelme, 2018, pp. 54-55), o
  - patrimonio <= 0: pasivos mayores que activos (Riquelme, 2018, p. 116).

Salida: cmf_empresas_reales.csv (liviano, sí va a git).
"""
import csv
import glob
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)

from AppWeb.datos_macro import cargar_indicadores_macro  # noqa: E402
from AppWeb.variables_modelo import UMBRAL_ZEM_INSOLVENCIA, calcular_variables_financieras, calcular_zem_altman  # noqa: E402

CMF_DIR = os.path.join(RAIZ, 'DatasetEntrenamientoML', 'chile_cmf_boletin', 'cmf_raw')
QUIEBRAS_REALES_CSV = os.path.join(RAIZ, 'DatasetEntrenamientoML', 'chile_cmf_boletin', 'resultado_interseccion.csv')
SALIDA = os.path.join(AQUI, 'cmf_empresas_reales.csv')

# Cuenta IFRS de la CMF -> columna de la plantilla del sistema (RF-08)
CUENTAS_BALANCE = {
    'Activos corrientes totales': 'Activo_Circulante',
    'Pasivos corrientes totales': 'Pasivo_Circulante',
    'Total de activos': 'Activo_Total',
    'Total de pasivos': 'Pasivo_Total',
    'Patrimonio total': 'Patrimonio_Neto',
    'Ganancias (pérdidas) acumuladas': 'Utilidades_Retenidas',
}
CUENTAS_RESULTADO = {
    'Ingresos de actividades ordinarias': 'Ingresos_Netos',
    'Ganancias (pérdidas) de actividades operacionales': 'Resultado_Operacional',
    'Ganancia (pérdida), antes de impuestos': 'Ganancia_Antes_Impuestos',
    'Costos financieros': 'Costos_Financieros',
}
TAXONOMIAS_RESULTADO = {'ERFG', 'ERNG'}  # estado de resultados por función o por naturaleza
REQUERIDAS = list(CUENTAS_BALANCE.values()) + ['Ingresos_Netos']


def normalizar_rut(rut: str) -> str:
    rut = str(rut).strip().upper().replace('.', '').replace(' ', '').split('-')[0]
    return rut.lstrip('0') or '0'


def leer_cuentas_diciembre() -> dict:
    """(rut, año, tipo) -> {columna: valor}, con tipo C (consolidado) o I (individual)."""
    datos = {}
    for ruta in sorted(glob.glob(os.path.join(CMF_DIR, 'eifrs_*.txt'))):
        with open(ruta, encoding='utf-8', errors='replace') as f:
            for linea in f:
                campos = linea.rstrip('\n').split(';')
                if len(campos) < 9 or not campos[0].endswith('12'):
                    continue
                periodo, rut, razon, tipo, _moneda, cuenta, valor, _tax, taxonomia = campos[:9]
                if taxonomia == 'ESF C/NC':
                    columna = CUENTAS_BALANCE.get(cuenta)
                elif taxonomia in TAXONOMIAS_RESULTADO:
                    columna = CUENTAS_RESULTADO.get(cuenta)
                else:
                    columna = None
                if not columna:
                    continue
                try:
                    valor = float(valor)
                except ValueError:
                    continue
                clave = (normalizar_rut(rut), int(periodo[:4]), tipo)
                registro = datos.setdefault(clave, {'razon_social': razon})
                registro.setdefault(columna, valor)  # las cuentas repetidas traen el mismo valor
    return datos


def ebit(registro: dict):
    """Resultado operacional si la empresa lo informa; si no, la definición de
    Altman (1968): ganancia antes de impuestos + costos financieros."""
    if 'Resultado_Operacional' in registro:
        return registro['Resultado_Operacional']
    if 'Ganancia_Antes_Impuestos' in registro:
        return registro['Ganancia_Antes_Impuestos'] + abs(registro.get('Costos_Financieros', 0.0))
    return None


def main():
    datos = leer_cuentas_diciembre()
    macro = cargar_indicadores_macro()
    with open(QUIEBRAS_REALES_CSV, encoding='utf-8') as f:
        quiebras_reales = {normalizar_rut(r['rut_normalizado']) for r in csv.DictReader(f)}

    filas = []
    for (rut, anio, tipo), registro in datos.items():
        # Si la empresa informa consolidado e individual, se usa el consolidado.
        if tipo != 'C' and (rut, anio, 'C') in datos:
            continue
        registro = {**registro, 'EBIT': ebit(registro)}
        if registro['EBIT'] is None or any(c not in registro for c in REQUERIDAS):
            continue
        if registro['Activo_Total'] <= 0 or registro['Ingresos_Netos'] < 0:
            continue

        trimestre = f'{anio}-Q4'
        if trimestre not in macro.index:
            continue
        variables = calcular_variables_financieras(registro)
        zem = calcular_zem_altman(registro)
        filas.append({
            'rut': rut,
            'razon_social': registro['razon_social'],
            'anio': anio,
            **variables,
            **macro.loc[trimestre].to_dict(),
            'utilidades_retenidas_sobre_activos': registro['Utilidades_Retenidas'] / registro['Activo_Total'],
            'patrimonio_negativo': int(registro['Patrimonio_Neto'] <= 0),
            'zem_altman': zem,
            'insolvente': int(zem < UMBRAL_ZEM_INSOLVENCIA or registro['Patrimonio_Neto'] <= 0),
            'quiebra_real_boletin': int(rut in quiebras_reales),
        })

    df = pd.DataFrame(filas).sort_values(['rut', 'anio'])
    df.to_csv(SALIDA, index=False, float_format='%.6f')
    print(f'{len(df)} empresa-año de {df["rut"].nunique()} empresas ({df["anio"].min()}-{df["anio"].max()})')
    print(f'Insolventes por regla: {df["insolvente"].sum()} ({df["insolvente"].mean():.1%})'
          f' | por Z"EM: {(df["zem_altman"] < UMBRAL_ZEM_INSOLVENCIA).sum()}'
          f' | por patrimonio <= 0: {df["patrimonio_negativo"].sum()}')
    print(f'Filas de empresas con quiebra real (Boletín Concursal): {df["quiebra_real_boletin"].sum()}'
          f' ({df.loc[df["quiebra_real_boletin"] == 1, "rut"].nunique()} empresas)')


if __name__ == '__main__':
    main()
