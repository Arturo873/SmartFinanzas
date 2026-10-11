"""Agrega las columnas de la plantilla v8 (Ingresos_Netos, EBIT,
Utilidades_Retenidas) a carga_masiva_sintetica_5k.csv, para probar la carga
(RF-08, RF-09) y el rendimiento (RNF-04) con el formato nuevo.

Son datos de prueba inventados, no estados financieros reales.
"""
import os

import numpy as np
import pandas as pd

CARPETA = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(42)

df = pd.read_csv(os.path.join(CARPETA, 'carga_masiva_sintetica_5k.csv'))
n = len(df)
df['Ingresos_Netos'] = (df['Activo_Total'] * rng.uniform(0.4, 1.6, n)).round(2)
# El resultado operacional se mueve con la utilidad neta, más un margen aleatorio.
df['EBIT'] = (df['Utilidad_Neta'] * 1.35 + df['Ingresos_Netos'] * rng.normal(0.02, 0.03, n)).round(2)
df['Utilidades_Retenidas'] = (df['Patrimonio_Neto'] * rng.uniform(-0.2, 0.6, n)).round(2)

df.to_csv(os.path.join(CARPETA, 'carga_masiva_sintetica_5k_v8.csv'), index=False)
print(f'{n} filas -> carga_masiva_sintetica_5k_v8.csv')
