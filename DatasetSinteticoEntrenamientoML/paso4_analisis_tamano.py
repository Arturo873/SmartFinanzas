"""Paso 4: evalúa el modelo por tamaño de empresa, para responder si sirve con
empresas pequeñas y medianas aunque la CMF reúna sobre todo empresas grandes.

1. Clasifica cada empresa-año por ventas anuales según la Ley 20.416: micro
   hasta 2.400 UF, pequeña hasta 25.000 UF, mediana hasta 100.000 UF, grande
   sobre 100.000 UF. Las ventas son los "Ingresos de actividades ordinarias"
   a diciembre; las empresas que reportan en dólares se pasan a pesos.
2. Evalúa en la prueba real, por tamaño, el modelo oficial (entrenado con
   todas las empresas) y un modelo entrenado solo con empresa-año PYME.

La UF y el dólar son valores aproximados de cierre de cada año; bastan para
clasificar por tramo, pero una empresa cerca de un límite puede cambiar de
tramo con otro valor.

Requiere los archivos crudos de la CMF (ver paso 1). Solo imprime resultados.
"""
import glob
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)

from AppWeb.variables_modelo import CLAVES_MODELO  # noqa: E402
from paso1_extraer_cmf import CMF_DIR, normalizar_rut  # noqa: E402
from paso3_entrenar_evaluar import metricas, nuevo_random_forest  # noqa: E402

UF_CIERRE = {
    2012: 22840, 2013: 23310, 2014: 24628, 2015: 25629, 2016: 26348, 2017: 26799, 2018: 27566,
    2019: 28310, 2020: 29070, 2021: 30991, 2022: 35111, 2023: 36790, 2024: 38417,
}
DOLAR_CIERRE = {
    2012: 479, 2013: 524, 2014: 607, 2015: 707, 2016: 667, 2017: 615, 2018: 695,
    2019: 745, 2020: 711, 2021: 845, 2022: 856, 2023: 877, 2024: 996,
}
TAMANOS_PYME = ['Micro', 'Pequeña', 'Mediana']


def leer_ventas_uf() -> dict:
    """(rut, año, tipo) -> ventas anuales en UF, con tipo C (consolidado) o I (individual)."""
    ventas = {}
    for ruta in sorted(glob.glob(os.path.join(CMF_DIR, 'eifrs_*.txt'))):
        with open(ruta, encoding='utf-8', errors='replace') as f:
            for linea in f:
                campos = linea.rstrip('\n').split(';')
                if len(campos) < 9 or not campos[0].endswith('12') or campos[5] != 'Ingresos de actividades ordinarias':
                    continue
                anio = int(campos[0][:4])
                if anio not in UF_CIERRE:
                    continue
                try:
                    valor = float(campos[6])
                except ValueError:
                    continue
                pesos = valor * DOLAR_CIERRE[anio] if campos[4] == 'USD' else valor
                ventas.setdefault((normalizar_rut(campos[1]), anio, campos[3]), pesos / UF_CIERRE[anio])
    return ventas


def tamano(ventas_uf):
    if ventas_uf is None:
        return None
    if ventas_uf <= 2_400:
        return 'Micro'
    if ventas_uf <= 25_000:
        return 'Pequeña'
    if ventas_uf <= 100_000:
        return 'Mediana'
    return 'Grande'


def agregar_tamano(df: pd.DataFrame, ventas: dict) -> pd.DataFrame:
    # Igual que en el paso 1: consolidado si existe, si no individual.
    def ventas_de(fila):
        for tipo in ('C', 'I'):
            clave = (normalizar_rut(str(fila.rut)), fila.anio, tipo)
            if clave in ventas:
                return ventas[clave]
        return None
    return df.assign(tamano=[tamano(ventas_de(fila)) for fila in df.itertuples()])


def main():
    ventas = leer_ventas_uf()
    entrenamiento = agregar_tamano(pd.read_csv(os.path.join(AQUI, 'real_entrenamiento.csv')), ventas)
    prueba = agregar_tamano(pd.read_csv(os.path.join(AQUI, 'real_prueba.csv')), ventas)

    todo = pd.concat([entrenamiento, prueba], ignore_index=True)
    print('Empresa-año por tamaño (insolvente 0/1):')
    print(pd.crosstab(todo['tamano'].fillna('Sin ventas'), todo['insolvente'], margins=True).to_string())
    pyme = todo[todo['tamano'].isin(TAMANOS_PYME)]
    print(f'Empresas con algún año PYME: {pyme["rut"].nunique()} de {todo["rut"].nunique()}')

    # Como en el sistema: sin datos de caja, V7 neutra.
    volatilidad_neutra = float(entrenamiento.loc[entrenamiento['insolvente'] == 0, 'volatilidad_flujo_caja'].median())
    prueba = prueba.assign(volatilidad_flujo_caja=volatilidad_neutra)

    entrenamiento_pyme = entrenamiento[entrenamiento['tamano'].isin(TAMANOS_PYME)]
    modelos = {
        'todas las empresas (oficial)': nuevo_random_forest().fit(entrenamiento[CLAVES_MODELO], entrenamiento['insolvente']),
        'solo empresa-año PYME': nuevo_random_forest().fit(entrenamiento_pyme[CLAVES_MODELO], entrenamiento_pyme['insolvente']),
    }
    print(f'\nEntrenamiento solo PYME: {len(entrenamiento_pyme)} empresa-año, '
          f'{int(entrenamiento_pyme["insolvente"].sum())} insolventes')

    subconjuntos = {
        'Prueba completa': prueba,
        'Prueba PYME': prueba[prueba['tamano'].isin(TAMANOS_PYME)],
        'Prueba grandes': prueba[prueba['tamano'] == 'Grande'],
    }
    print('\nPrueba real sin datos de caja:')
    for nombre_prueba, datos in subconjuntos.items():
        print(f'{nombre_prueba}: {len(datos)} empresa-año, {int(datos["insolvente"].sum())} insolventes')
        for nombre_modelo, modelo in modelos.items():
            resultado = metricas(datos['insolvente'], modelo.predict_proba(datos[CLAVES_MODELO])[:, 1])
            print(f'  entrenado con {nombre_modelo}:', {k: round(v * 100, 1) for k, v in resultado.items()})


if __name__ == '__main__':
    main()
