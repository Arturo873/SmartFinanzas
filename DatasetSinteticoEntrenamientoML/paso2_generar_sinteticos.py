"""Paso 2: datasets sintéticos en 5 proporciones (Acta CreaEmpresas 05-10-2026).

1. Separa las empresas reales de la CMF en entrenamiento (80 %) y prueba real
   (20 %), por empresa, para que ninguna empresa de la prueba aporte datos al
   entrenamiento. Las 3 empresas con quiebra real (Boletín Concursal) van
   siempre a la prueba.
2. Simula V7 (volatilidad del flujo de caja), que no existe en datos públicos.
3. Genera cada dataset con Borderline-SMOTE (Han et al., 2005) a partir de las
   empresas reales de entrenamiento, y filtra los casos sintéticos con las
   reglas axiomáticas del tablero Miro.

Proporciones insolventes/solventes: 50/50, 40/60, 30/70, 20/80 y 10/90.

Salidas: real_entrenamiento.csv, real_prueba.csv y sintetico_XX_YY.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
from imblearn.over_sampling import BorderlineSMOTE
from sklearn.model_selection import StratifiedGroupKFold

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

from AppWeb.variables_modelo import (  # noqa: E402
    CLAVES_MODELO,
    LEVERAGE_MAXIMO,
    MARGEN_OPERACIONAL_LIMITE,
    RAZON_CORRIENTE_MAXIMA,
    ROTACION_ACTIVOS_MAXIMA,
)

SEMILLA = 42
TOTAL_POR_DATASET = 10_000
PROPORCIONES_INSOLVENTES = [0.50, 0.40, 0.30, 0.20, 0.10]
# Se piden más sintéticos de los necesarios porque las reglas axiomáticas
# descartan una parte.
HOLGURA_SINTETICOS = 1.3

# Supuesto de simulación de V7 (no hay datos públicos de flujo de caja diario):
# log(V7) = log(base) + pendiente * leverage + ruido. La dirección (más deuda,
# más volatilidad) sigue a Ringeling (2004, p. 87); base, pendiente y ruido
# son supuestos de diseño, declarados como limitación.
V7_BASE = 0.30
V7_PENDIENTE_LEVERAGE = 0.10
V7_RUIDO = 0.35


def simular_volatilidad(df: pd.DataFrame, rng) -> pd.Series:
    log_v7 = np.log(V7_BASE) + V7_PENDIENTE_LEVERAGE * df['leverage_total'] + rng.normal(0, V7_RUIDO, len(df))
    return pd.Series(np.exp(log_v7), index=df.index)


def separar_entrenamiento_prueba(df: pd.DataFrame):
    con_quiebra_real = df.groupby('rut')['quiebra_real_boletin'].transform('max') == 1
    resto = df[~con_quiebra_real]
    # Estratificado por etiqueta y agrupado por empresa: 1 de 5 pliegues = 20 %.
    pliegues = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    idx_entrenamiento, idx_prueba = next(pliegues.split(resto, resto['insolvente'], groups=resto['rut']))
    entrenamiento = resto.iloc[idx_entrenamiento]
    prueba = pd.concat([resto.iloc[idx_prueba], df[con_quiebra_real]])
    return entrenamiento, prueba


def cumple_reglas_axiomaticas(df: pd.DataFrame) -> pd.Series:
    """Reglas axiomáticas del Miro sobre los casos sintéticos."""
    rc, cta = df['razon_corriente'], df['capital_trabajo_sobre_activos']
    return (
        rc.between(0, RAZON_CORRIENTE_MAXIMA)
        # Razón corriente > 1 si y solo si el capital de trabajo es positivo.
        & (((rc > 1) == (cta > 0)) | (cta.abs() < 1e-3))
        & df['leverage_total'].between(0, LEVERAGE_MAXIMO)
        & df['rotacion_activos'].between(0, ROTACION_ACTIVOS_MAXIMA)
        & df['margen_operacional'].between(-MARGEN_OPERACIONAL_LIMITE, MARGEN_OPERACIONAL_LIMITE)
        & (df['volatilidad_flujo_caja'] >= 0)
    )


def generar_dataset(reales: pd.DataFrame, prop_insolventes: float) -> pd.DataFrame:
    objetivo = {1: int(round(TOTAL_POR_DATASET * prop_insolventes))}
    objetivo[0] = TOTAL_POR_DATASET - objetivo[1]

    # Si hay más empresas reales de una clase que las pedidas, se submuestrea.
    base = pd.concat([
        grupo.sample(n=min(len(grupo), objetivo[clase]), random_state=SEMILLA)
        for clase, grupo in reales.groupby('insolvente')
    ])
    pedido = {
        clase: len(base[base['insolvente'] == clase])
        + int((objetivo[clase] - len(base[base['insolvente'] == clase])) * HOLGURA_SINTETICOS)
        for clase in (0, 1)
    }
    smote = BorderlineSMOTE(sampling_strategy=pedido, k_neighbors=5, m_neighbors=10, random_state=SEMILLA)
    x, y = smote.fit_resample(base[CLAVES_MODELO], base['insolvente'])

    generado = pd.DataFrame(x, columns=CLAVES_MODELO)
    generado['insolvente'] = y.values
    generado['origen'] = ['real'] * len(base) + ['sintetico'] * (len(generado) - len(base))

    sinteticos = generado['origen'] == 'sintetico'
    # Identidad DuPont: ROA = margen operacional x rotación de activos. La
    # interpolación lineal de SMOTE la rompe, así que se recalcula.
    generado.loc[sinteticos, 'roa_operacional'] = (
        generado.loc[sinteticos, 'margen_operacional'] * generado.loc[sinteticos, 'rotacion_activos']
    )
    validos = ~sinteticos | cumple_reglas_axiomaticas(generado)
    descartados = int((~validos).sum())
    generado = generado[validos]

    # Se conservan todas las empresas reales y se completa con sintéticos.
    partes = []
    for clase in (0, 1):
        de_clase = generado[generado['insolvente'] == clase]
        reales_clase = de_clase[de_clase['origen'] == 'real']
        faltan = objetivo[clase] - len(reales_clase)
        partes += [reales_clase, de_clase[de_clase['origen'] == 'sintetico'].sample(n=faltan, random_state=SEMILLA)]
    dataset = pd.concat(partes).sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
    return dataset, descartados


def main():
    rng = np.random.default_rng(SEMILLA)
    reales = pd.read_csv(os.path.join(AQUI, 'cmf_empresas_reales.csv'))
    reales['volatilidad_flujo_caja'] = simular_volatilidad(reales, rng)

    entrenamiento, prueba = separar_entrenamiento_prueba(reales)
    entrenamiento.to_csv(os.path.join(AQUI, 'real_entrenamiento.csv'), index=False, float_format='%.6f')
    prueba.to_csv(os.path.join(AQUI, 'real_prueba.csv'), index=False, float_format='%.6f')
    print(f'Reales de entrenamiento: {len(entrenamiento)} filas, {entrenamiento["rut"].nunique()} empresas, '
          f'{entrenamiento["insolvente"].sum()} insolventes')
    print(f'Reales de prueba:        {len(prueba)} filas, {prueba["rut"].nunique()} empresas, '
          f'{prueba["insolvente"].sum()} insolventes')

    for prop in PROPORCIONES_INSOLVENTES:
        dataset, descartados = generar_dataset(entrenamiento, prop)
        nombre = f'sintetico_{round(prop * 100)}_{round((1 - prop) * 100)}.csv'
        dataset.to_csv(os.path.join(AQUI, nombre), index=False, float_format='%.6f')
        conteo = dataset.groupby(['insolvente', 'origen']).size().to_dict()
        print(f'{nombre}: {len(dataset)} filas {conteo} | sintéticos descartados por reglas axiomáticas: {descartados}')


if __name__ == '__main__':
    main()
