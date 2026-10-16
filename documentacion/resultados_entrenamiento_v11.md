# Resultados del entrenamiento del modelo v11 (RNF-08)

Modelo de 7 variables entrenado **solo con empresas chilenas reales de la CMF**. Fecha: 2026-10-16. Reemplaza al modelo v10, que usaba las mismas 7 variables pero se entrenaba con datos sintéticos (Borderline-SMOTE en proporción 50/50). Las cifras de los modelos v8 y v10 quedan en la [bitácora](bitacora_modelo_v8.md).
Scripts en `DatasetSinteticoEntrenamientoML/`. Fuentes citadas (R1-R10) en [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

## 1. Resumen

| Pregunta | Resultado |
|---|---|
| Con qué se entrena | 542 empresas reales de la CMF (4.211 empresa-año, 185 insolventes), sin datos sintéticos |
| Cómo se valida | Prueba con **136 empresas reales que el modelo nunca vio** (1.066 empresa-año, 51 insolventes) |
| Resultado en el sistema actual (sin datos de caja) | **Accuracy 97,8 %, F1 76,8 %, Recall 74,5 %, Precisión 79,2 %, PR-AUC 85,8 %** |
| ¿Los sintéticos mejoran el resultado? | No: en la misma prueba real, el F1 queda igual (71-76 %) y el PR-AUC baja (80-82 % contra 85,5 %) |
| ¿Sirve con empresas pequeñas y medianas? | En las PYMEs por ventas de la prueba, F1 = 94,4 % (contra 66,7 % en las grandes) |
| Nstock | Reservado para validar el sistema con una PYME real; no se usó |

**Por qué se dejaron los sintéticos:** el profesor del curso pidió que la evidencia de precisión y generalización salga de datos reales, no sintéticos. Al entrenar solo con datos reales, el resultado con empresas nunca vistas es igual o mejor que con cualquier proporción sintética. Los datasets sintéticos del Acta CreaEmpresas (05-10-2026) se conservan como comparación (sección 3.2).

## 2. Metodología

### 2.1 Base real: empresas de la CMF

- **Origen:** estados financieros IFRS que las empresas reportan a la CMF, balance a diciembre (flujos de 12 meses), 2012-2024.
- **Muestra:** 5.277 empresa-año de 678 empresas no financieras (con balance clasificado en corriente y no corriente).
- **Variables:** V1 a V6, calculadas con `AppWeb/variables_modelo.py`, el mismo código que usa el sistema. V7 se simula (sección 2.4).
- **EBIT:** se usa el resultado de actividades operacionales; si la empresa no lo informa, ganancia antes de impuestos + costos financieros (definición de Altman, 1968).
- **Años:** los archivos de la CMF van de 2009 a 2024, pero 2009-2011 quedan fuera. En 2010 y 2011 falta la cuenta "Total de pasivos" (unas 430 y 590 empresas), y 2009 usa nombres de cuenta antiguos ("Activos, Total", "Patrimonio Neto, Total"). Se podrían recuperar calculando el pasivo como activo menos patrimonio y agregando los nombres antiguos; quedó como trabajo futuro.

### 2.2 Etiqueta: zona de insolvencia según Altman

Una empresa-año es **insolvente** si cumple al menos una de estas condiciones:
- **Z''EM < 1,10:** Z-score de Altman para mercados emergentes (Altman et al., 2017; citado en R2, pp. 54-55). Hay 171 casos.
- **Patrimonio ≤ 0:** pasivos mayores que activos, es decir, insolvencia contable (R2, p. 116). Hay 150 casos.

En total, **236 empresa-año insolventes (4,5 %)**. "Insolvente" significa *en zona de riesgo de insolvencia según Altman*, no quiebra legal. Las quiebras legales con estados financieros públicos son solo 3 (cruce CMF × Boletín Concursal), demasiado pocas para entrenar; la zona de riesgo de Altman entrega 236 casos reales.

**Por qué Z''EM y no Z1:** Z1 marca al 40 % de las empresas de la CMF, porque castiga la baja rotación de activos típica de sociedades de inversión, eléctricas e inmobiliarias. El detalle está en [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

### 2.3 Separación entrenamiento / prueba real

Las empresas se separaron **por empresa** (`StratifiedGroupKFold`, 1 de 5 pliegues), para que ninguna aporte datos a la vez al entrenamiento y a la prueba:

| Conjunto | Empresas | Empresa-año | Insolventes |
|---|---|---|---|
| Entrenamiento | 542 | 4.211 | 185 (4,4 %) |
| Prueba real (nunca vista) | 136 | 1.066 | 51 (4,8 %) |

Las 3 empresas con quiebra legal según el Boletín Concursal se dejaron siempre en la prueba.

### 2.4 V7 simulada

No existen datos públicos de flujo de caja diario. En las empresas de la CMF, V7 se simuló como `log(V7) = log(0,30) + 0,10 · leverage + ruido normal(0; 0,35)`. La dirección (más deuda, más volatilidad) sigue a Ringeling (2004, p. 87); los parámetros son supuestos de diseño.

Como el módulo de caja (RF-19 a RF-22) no está implementado, el sistema usa **V7 neutra** para todas las empresas: la mediana de las solventes de entrenamiento (0,341). Por eso la cifra principal se mide con V7 neutra.

### 2.5 Entrenamiento y evaluación

- Random Forest (Breiman, 2001) de 300 árboles con `min_samples_leaf = 2`; umbral de clasificación 0,5. Se entrena con la proporción natural de insolventes (4,4 %), sin balanceo.
- **Prueba real:** las 136 empresas reservadas, con su proporción natural de insolventes (4,8 %).
- **Comparación con sintéticos:** con los mismos parámetros, un modelo por cada dataset sintético del Acta (50/50, 40/60, 30/70, 20/80 y 10/90; Borderline-SMOTE + reglas axiomáticas, generados en `paso2_generar_sinteticos.py`). Cada uno se evalúa en su 20 % sintético y en la misma prueba real.

## 3. Resultados

### 3.1 Modelo oficial en la prueba real

| | Accuracy | F1 | Recall | Precisión | PR-AUC |
|---|---|---|---|---|---|
| Con V7 simulada | 97,7 % | 75,7 % | 76,5 % | 75,0 % | 85,5 % |
| **Con V7 neutra (sistema actual)** | **97,8 %** | **76,8 %** | **74,5 %** | **79,2 %** | **85,8 %** |

El Accuracy es alto en cualquier modelo porque el 95 % de los casos son solventes; las métricas que importan son F1, Recall y PR-AUC de la clase insolvente.

### 3.2 Comparación: datos reales contra sintéticos

Todos se evalúan en la misma prueba real, con V7 simulada.

| Entrenado con | F1 real | Recall real | Precisión real | PR-AUC real | F1 en su prueba sintética |
|---|---|---|---|---|---|
| **Solo reales (oficial)** | 75,7 % | 76,5 % | 75,0 % | **85,5 %** | — |
| Sintético 50/50 | 76,2 % | 78,4 % | 74,1 % | 81,6 % | 98,4 % |
| Sintético 40/60 | 74,5 % | 74,5 % | 74,5 % | 79,5 % | 98,7 % |
| Sintético 30/70 | 75,5 % | 78,4 % | 72,7 % | 81,8 % | 98,1 % |
| Sintético 20/80 | 71,2 % | 72,5 % | 69,8 % | 80,7 % | 97,1 % |
| Sintético 10/90 | 72,0 % | 70,6 % | 73,5 % | 81,7 % | 92,7 % |

**Lectura:**
- **El F1 real es prácticamente igual** con o sin sintéticos. Con 51 insolventes en la prueba, cada caso mueve el F1 unos 2 puntos, así que diferencias de 1-2 puntos son ruido.
- **El PR-AUC es mejor con solo reales** (85,5 % contra 79-82 %). El PR-AUC mide qué tan bien el modelo ordena a las empresas de más a menos riesgo, sin depender del umbral; los sintéticos empeoran esa calidad.
- **La prueba sintética es optimista** (92-99 %): mide al modelo con datos generados desde las mismas empresas y reglas que el entrenamiento. Por eso no se usa como evidencia.
- **Lo que pedía el Acta** (fluctuación por proporción): en la prueba sintética el F1 baja de 98,4 % a 92,7 % con menos insolventes; en la prueba real casi no cambia (71-76 %).

### 3.3 Por tamaño de empresa

La CMF reúne sobre todo empresas grandes. Para ver si el modelo sirve con empresas pequeñas y medianas, `paso4_analisis_tamano.py` clasifica cada empresa-año por ventas anuales según la Ley 20.416 (micro ≤ 2.400 UF, pequeña ≤ 25.000 UF, mediana ≤ 100.000 UF). Las ventas en dólares se pasan a pesos, con UF y dólar aproximados de cierre de cada año.

| Tamaño | Empresa-año | Insolventes |
|---|---|---|
| Grande | 4.097 | 161 |
| Mediana | 540 | 31 |
| Pequeña | 452 | 37 |
| Micro | 188 | 7 |

**1.180 empresa-año (22 %) de 227 empresas** son micro, pequeñas o medianas por ventas, con 75 insolventes.

Prueba real, sin datos de caja:

| Se evalúa en | Entrenado con todas (oficial) | Entrenado solo con PYMEs (929 empresa-año, 57 insolventes) |
|---|---|---|
| Prueba completa (51 insolventes) | **F1 76,8 %**, Recall 74,5 % | F1 76,1 %, Recall 68,6 % |
| PYMEs de la prueba (251 empresa-año, 18 insolventes) | **F1 94,4 %**, Recall 94,4 % | F1 91,9 %, Recall 94,4 % |
| Grandes de la prueba (815 empresa-año, 33 insolventes) | **F1 66,7 %**, Recall 63,6 % | F1 65,5 %, Recall 54,5 % |

**Lectura:**
- **El modelo no empeora con empresas más chicas:** con las PYMEs de la prueba rinde mejor que con las grandes. Con solo 18 insolventes PYME, el 94,4 % es una señal, no una cifra precisa.
- **Entrenar solo con PYMEs es peor** en los tres conjuntos: pierde 128 casos de insolvencia para aprender. Por eso el modelo oficial usa todas las empresas.
- **"PYME por ventas" no es una PYME típica:** incluye holdings, inmobiliarias y empresas del Estado que reportan a la CMF.
- **Por qué funciona con distintos tamaños:** las 7 variables son razones financieras (V7 se divide por el ingreso promedio diario, RNF-10), así que no dependen de la escala en pesos. Esto reduce la diferencia entre empresas grandes y PYMEs, pero no la elimina: sus ratios siguen teniendo distribuciones distintas.

### 3.4 Importancia de las variables

| Variable | Importancia |
|---|---|
| Leverage total (V3) | 31,8 % |
| Capital de trabajo sobre activos (V2) | 18,0 % |
| ROA operacional (V4) | 14,9 % |
| Margen operacional (V5) | 10,2 % |
| Volatilidad del flujo de caja (V7, simulada) | 10,0 % |
| Razón corriente (V1) | 8,8 % |
| Rotación de activos (V6) | 6,3 % |

V7 se simuló a partir del leverage, así que su importancia refleja en parte al leverage y no un efecto propio de la volatilidad.

### 3.5 Chequeo ilustrativo con quiebras legales reales

Son solo 3 casos, así que **no permiten calcular métricas**; se muestran como evidencia cualitativa.

| Empresa (último año con datos) | Z''EM | Etiqueta | Probabilidad del modelo |
|---|---|---|---|
| Sartor Administradora General de Fondos (2024) | −15,4 | Insolvente | 0,98 |
| Telecomunicaciones Internacionales (2014) | −15,5 | Insolvente | 0,92 |
| Claro, Vicuña, Valenzuela (2014) | 4,5 | Solvente | 0,01 |

El modelo detecta a 2 de las 3. La tercera solo tiene datos hasta 2014, probablemente varios años antes de su quiebra, cuando sus cifras todavía eran sanas.

## 4. Limitaciones (declarar en el informe)

1. **La etiqueta es la zona de riesgo de Altman, no la quiebra legal.** Z''EM usa capital de trabajo / activos y EBIT / activos, que también son V2 y V4; parte de lo que aprende el modelo es reconstruir esa fórmula. Por eso el F1 (≈ 77 %) no es comparable con el 46,8 % del modelo de Taiwán, que se medía contra quiebras legales.
2. **Las empresas de la CMF no son PYMEs típicas.** Son sociedades que reportan a la CMF; las PYMEs por ventas que hay entre ellas (22 %) incluyen holdings, inmobiliarias y empresas del Estado. No existen balances públicos de PYMEs chilenas: el SII solo publica tramos de ventas y el Boletín Concursal no trae cifras.
3. **V7 es simulada** y el sistema todavía no la calcula, porque no existe el módulo de caja.
4. **La prueba es chica en la clase insolvente:** 51 casos (18 PYME), así que las cifras tienen un margen de varios puntos.
5. **El dato de la plantilla debe ser de 12 meses.** El modelo se entrenó con flujos anuales, así que Ingresos_Netos, EBIT y Utilidad_Neta deben corresponder a los últimos 12 meses.

## 5. Cómo reproducirlo

```
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso1_extraer_cmf.py         (requiere cmf_raw local)
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso2_generar_sinteticos.py
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso3_entrenar_evaluar.py
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso4_analisis_tamano.py     (requiere cmf_raw local)
```

El paso 2 separa entrenamiento y prueba (`real_entrenamiento.csv`, `real_prueba.csv`) y genera los sintéticos de comparación. El paso 3 entrena el modelo oficial y lo guarda en `AppWeb/modelo_oficial/modelo_riesgo_v11.joblib` y `metricas_v11.joblib`. Los pasos 1 y 4 necesitan los archivos crudos de la CMF (`DatasetEntrenamientoML/chile_cmf_boletin/cmf_raw/`), que no están en git por su tamaño. La salida del paso 1, `cmf_empresas_reales.csv`, sí está en git, así que los pasos 2 y 3 se pueden repetir sin los crudos. Todo usa la semilla 42.
