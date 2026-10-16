# Resultados del entrenamiento del modelo v10 (RNF-08)

Modelo de 7 variables (Requerimientos v10). Fecha: 2026-10-16. Reemplaza al modelo v8 de 8 variables (Fase 4 del plan "camino 3", 2026-10-11), que además usaba el contexto macroeconómico (V8). Las cifras del modelo v8 quedan en la [bitácora](bitacora_modelo_v8.md).
Scripts en `DatasetSinteticoEntrenamientoML/`. Fuentes citadas (R1-R10) en [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

## 1. Resumen

| Requisito (RNF-08 / Acta 05-10-2026) | Resultado |
|---|---|
| Random Forest entrenado desde cero | Sí (Breiman, 2001), 300 árboles |
| Datos sintéticos en varias proporciones | 5 datasets de 10.000 filas: 50/50, 40/60, 30/70, 20/80 y 10/90 (insolventes/solventes) |
| Meta mínima de 90 % en Accuracy y F1 | **Cumplen las 5** proporciones; la más baja es 10/90, con F1 = 92,7 % |
| Meta ideal de 95 % | **Modelo elegido (50/50): Accuracy 98,4 %, F1 98,4 %, Recall 99,5 %** |
| Nstock reservado para validación posterior | Sí, no se usó |

**Cifra realista con empresas reales:** sobre empresas chilenas de la CMF que el modelo nunca vio, y sin datos de caja (como funciona hoy el sistema), el modelo elegido logra **Accuracy 97,4 %, F1 73,6 % y Recall 76,5 %**.

## 2. Metodología

### 2.1 Base real: empresas de la CMF

- **Origen:** estados financieros IFRS que las empresas reportan a la CMF, balance a diciembre (flujos de 12 meses), 2012-2024.
- **Muestra:** 5.277 empresa-año de 678 empresas no financieras (con balance clasificado en corriente y no corriente).
- **Variables:** V1 a V6, calculadas con `AppWeb/variables_modelo.py`, el mismo código que usa el sistema. V7 se simula en el paso 2.
- **EBIT:** se usa el resultado de actividades operacionales; si la empresa no lo informa, ganancia antes de impuestos + costos financieros (definición de Altman, 1968).

### 2.2 Etiqueta: zona de insolvencia según Altman

Una empresa-año es **insolvente** si cumple al menos una de estas condiciones:
- **Z''EM < 1,10:** Z-score de Altman para mercados emergentes (Altman et al., 2017; citado en R2, pp. 54-55). Hay 171 casos.
- **Patrimonio ≤ 0:** pasivos mayores que activos, es decir, insolvencia contable (R2, p. 116). Hay 150 casos.

En total, **236 empresa-año insolventes (4,5 %)**. "Insolvente" significa *en zona de riesgo de insolvencia según Altman*, no quiebra legal.

**Por qué Z''EM y no Z1:** Z1 marca al 40 % de las empresas de la CMF, porque castiga la baja rotación de activos típica de sociedades de inversión, eléctricas e inmobiliarias. El detalle está en [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

### 2.3 Separación entrenamiento / prueba real

**Antes de generar datos sintéticos**, las empresas se separaron **por empresa**, para que ninguna aporte datos a la vez al entrenamiento y a la prueba:

| Conjunto | Empresas | Empresa-año | Insolventes |
|---|---|---|---|
| Entrenamiento (base de los sintéticos) | 542 | 4.211 | 185 |
| Prueba real (nunca vista) | 136 | 1.066 | 51 |

Las 3 empresas con quiebra legal según el Boletín Concursal se dejaron siempre en la prueba.

### 2.4 Generación sintética

1. **V7 simulada.** No existen datos públicos de flujo de caja diario. Se simuló como `log(V7) = log(0,30) + 0,10 · leverage + ruido normal(0; 0,35)`. La dirección (más deuda, más volatilidad) sigue a Ringeling (2004, p. 87); los parámetros son supuestos de diseño.
2. **Borderline-SMOTE** (Han et al., 2005; k = 5, m = 10) sobre las empresas reales de entrenamiento, hasta completar cada proporción. Si una clase tenía más empresas reales que las pedidas, se submuestreó.
3. **Identidad DuPont:** en los casos sintéticos, el ROA se recalcula como margen operacional × rotación de activos, porque la interpolación lineal de SMOTE rompe esa igualdad contable.
4. **Reglas axiomáticas** (tablero Miro): se descartaron los casos sintéticos que violan alguna de estas reglas:
   - razón corriente entre 0 y 10;
   - razón corriente > 1 si y solo si el capital de trabajo es positivo;
   - leverage, rotación y margen dentro de sus topes;
   - V7 ≥ 0.

   Se descartaron entre 54 y 152 casos por dataset. El modelo v8 tenía además la regla "en recesión (PIB < 0), ROA no mayor al percentil 99 real", que se quitó junto con el contexto macroeconómico.
5. Cada dataset conserva **todas las empresas reales** de entrenamiento y se completa con sintéticos.

### 2.5 Entrenamiento y evaluación

- Random Forest de 300 árboles con `min_samples_leaf = 2`; umbral de clasificación 0,5.
- **Prueba sintética:** 20 % de cada dataset, estratificado, separado antes de entrenar. Es la que exige RNF-08.
- **Prueba real:** las 136 empresas reservadas, con su proporción natural de insolventes (4,8 %).
- **Criterio de elección:** entre los modelos que cumplen la meta mínima en la prueba sintética, el de mayor F1 en la prueba real.

## 3. Resultados

| Proporción | Accuracy sint. | F1 sint. | Recall sint. | Accuracy real | F1 real | Recall real | Precisión real | PR-AUC real |
|---|---|---|---|---|---|---|---|---|
| **50/50 (elegido)** | **98,4 %** | **98,4 %** | **99,5 %** | 97,7 % | **76,2 %** | 78,4 % | 74,1 % | 81,6 % |
| 40/60 | 99,0 % | 98,7 % | 99,4 % | 97,6 % | 74,5 % | 74,5 % | 74,5 % | 79,5 % |
| 30/70 | 98,9 % | 98,1 % | 98,2 % | 97,6 % | 75,5 % | 78,4 % | 72,7 % | 81,8 % |
| 20/80 | 98,9 % | 97,1 % | 97,2 % | 97,2 % | 71,2 % | 72,5 % | 69,8 % | 80,7 % |
| 10/90 | 98,6 % | 92,7 % | 88,5 % | 97,4 % | 72,0 % | 70,6 % | 73,5 % | 81,7 % |

**Lectura (fluctuaciones de error y confianza que pide el Acta):**
- **En la prueba sintética,** el F1 baja a medida que las insolventes son minoría: 98,4 % con 50/50 y 92,7 % con 10/90. Hay menos ejemplos de la clase difícil.
- **En la prueba real,** el comportamiento es casi estable (F1 de 71-76 %). La proporción de entrenamiento cambia poco la capacidad de generalizar a empresas nuevas.
- **La diferencia entre ambas pruebas (≈ 98 % contra ≈ 76 %)** es la brecha esperable entre datos generados desde las mismas reglas y empresas reales que el modelo nunca vio.

### 3.1 Sin datos de caja (situación actual del sistema)

El módulo de caja (RF-19 a RF-22) no está implementado, así que el sistema usa V7 neutra para todas las empresas (mediana de las solventes = 0,341). Medido así en la prueba real:

| | Accuracy | F1 | Recall | Precisión | PR-AUC |
|---|---|---|---|---|---|
| Con V7 simulada | 97,7 % | 76,2 % | 78,4 % | 74,1 % | 81,6 % |
| **Con V7 neutra (hoy)** | **97,4 %** | **73,6 %** | **76,5 %** | **70,9 %** | **74,3 %** |

### 3.2 Importancia de las variables (modelo 50/50)

| Variable | Importancia |
|---|---|
| Leverage total (V3) | 25,7 % |
| ROA operacional (V4) | 17,7 % |
| Margen operacional (V5) | 17,4 % |
| Capital de trabajo sobre activos (V2) | 11,7 % |
| Razón corriente (V1) | 10,3 % |
| Rotación de activos (V6) | 8,7 % |
| Volatilidad del flujo de caja (V7, simulada) | 8,5 % |

En el modelo v8, los 3 indicadores macroeconómicos sumaban solo un 6,1 % de la importancia, en línea con Zurita (2008, p. 29): su efecto sobre la probabilidad de quiebra individual es pequeño. Al quitarlos, el F1 con empresas reales sin datos de caja subió de 69,7 % a 73,6 %.

### 3.3 Chequeo ilustrativo con quiebras legales reales

Son solo 3 casos, así que **no permiten calcular métricas**; se muestran como evidencia cualitativa.

| Empresa (último año con datos) | Z''EM | Etiqueta | Probabilidad del modelo |
|---|---|---|---|
| Sartor Administradora General de Fondos (2024) | −15,4 | Insolvente | 0,93 |
| Telecomunicaciones Internacionales (2014) | −15,5 | Insolvente | 0,88 |
| Claro, Vicuña, Valenzuela (2014) | 4,5 | Solvente | 0,09 |

El modelo detecta a 2 de las 3. La tercera solo tiene datos hasta 2014, probablemente varios años antes de su quiebra, cuando sus cifras todavía eran sanas.

## 4. Limitaciones (declarar en el informe)

1. **La etiqueta es la zona de riesgo de Altman, no la quiebra legal.** En Chile hay muy pocas quiebras legales con estados financieros públicos (3 empresas en la CMF). La validación con quiebras reales queda para la etapa con Nstock.
2. **La prueba sintética es optimista.** Los datos sintéticos salen de las mismas empresas y reglas que el entrenamiento; por eso la cifra con empresas reales nunca vistas es la más representativa.
3. **V7 es simulada** y el sistema todavía no la calcula, porque no existe el módulo de caja.
4. **Las empresas de la CMF son grandes** (sociedades anónimas), no PYMES como Nstock.
5. **El dato de la plantilla debe ser de 12 meses.** El modelo se entrenó con flujos anuales, así que Ingresos_Netos, EBIT y Utilidad_Neta deben corresponder a los últimos 12 meses.

## 5. Cómo reproducirlo

```
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso1_extraer_cmf.py         (requiere cmf_raw local)
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso2_generar_sinteticos.py
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso3_entrenar_evaluar.py
```

El paso 1 necesita los archivos crudos de la CMF (`DatasetEntrenamientoML/chile_cmf_boletin/cmf_raw/`), que no están en git por su tamaño. Su salida, `cmf_empresas_reales.csv`, sí está en git, así que los pasos 2 y 3 se pueden repetir sin los crudos. Todo usa la semilla 42.
