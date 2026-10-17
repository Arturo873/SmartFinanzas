Asunto: Propuesta formal SmartFinanzas: alcance, componente de ML, datos reales y validación

Estimado profesor Covarrubias:

Junto con saludarle, y agradeciendo sus observaciones, le enviamos la propuesta formal que nos solicitó: el alcance, los datos y el componente de Machine Learning del proyecto, y en la sección C, los cambios respecto del proyecto aprobado con su justificación.

Tomamos sus tres observaciones principales:

- **El Machine Learning sigue siendo el eje del proyecto.** Ningún cambio lo reduce o reemplaza; los cambios de alcance afectan solo a módulos que no alimentan al modelo.
- **El modelo ahora se entrena y se evalúa solo con datos reales de empresas chilenas.** Probamos los datos sintéticos que nos recomendó CreaEmpresas y no mejoraron el resultado con empresas reales, así que quedan solo como análisis complementario y no como evidencia de precisión.
- **La base de datos se amplió:** de una sola empresa (Nstock Importaciones) a 678 empresas chilenas reales de la CMF.

Respondemos punto por punto.

---

## A. Datos

### 1. Qué conjuntos de datos se usan

| Fuente | Uso |
|---|---|
| Estados financieros IFRS que las empresas reportan a la CMF (2012-2024) | **Entrenamiento y prueba del modelo**: 678 empresas chilenas no financieras, 5.277 empresa-año |
| Boletín Concursal | Cruce con la CMF para identificar quiebras legales (solo 3 empresas con estados financieros públicos; se usan como chequeo cualitativo) |
| Nstock Importaciones | Prueba del sistema completo con una PYME real (carga de datos, cálculo de variables y predicción) |

El SII se descartó porque solo publica tramos de ventas, sin balances ni estados de resultados.

### 2. Qué empresas o sectores representan

Son sociedades chilenas que reportan a la CMF, de distintos sectores (comercio, industria, energía, inmobiliario, servicios, entre otros). Casi todas son grandes, pero 227 de las 678 empresas (1.180 empresa-año) son micro, pequeñas o medianas según sus ventas (Ley 20.416).

Las 7 variables son razones financieras, así que no dependen del tamaño de la empresa en pesos. La profesora Carolina San Martín (Área de Administración y Negocios, INACAP) validó las 7 variables en la reunión del 14-10-2026.

### 3. Cómo se procesan

1. Se extraen el balance y el estado de resultados a diciembre de cada empresa y año.
2. Se calculan las variables V1 a V6 con el mismo código que usa la plataforma, para que el modelo vea exactamente lo mismo en el entrenamiento y en el uso real.
3. Se etiqueta cada empresa-año como **insolvente** si está en zona de riesgo según el Z-score de Altman para mercados emergentes (Z''EM < 1,10) o si tiene patrimonio negativo (Altman et al., 2017, citado en Riquelme, 2018). Resultan 236 empresa-año insolventes (4,5 %).
4. Se separan las empresas en entrenamiento (542) y prueba (136), **por empresa**: ninguna empresa aporta datos a ambos conjuntos.

En la plataforma, el contador carga los estados financieros en una plantilla Excel o CSV. El sistema valida el archivo (celdas vacías, tipos de datos, descuadres) y calcula las 7 variables antes de la predicción.

### 4. Por qué son pertinentes para el problema

No existen balances públicos de PYMEs chilenas quebradas: el SII no publica estados financieros y el Boletín Concursal no trae cifras. Las quiebras legales con estados financieros públicos son solo 3, demasiado pocas para entrenar un modelo (Zurita, 2008, reporta una probabilidad promedio de quiebra de 0,64 % en empresas chilenas).

Por eso el modelo aprende a reconocer la **zona de riesgo de insolvencia** de Altman, que entrega 236 casos reales en empresas chilenas. Además, el modelo rinde mejor con las empresas más pequeñas de la prueba (punto 5).

Sobre la escala del caso de estudio: los datos de una sola empresa patrocinadora no bastan para entrenar ni validar un modelo, y por eso la base de entrenamiento y prueba es la CMF y no Nstock. Esta base todavía se puede ampliar: los archivos de la CMF de 2009 a 2011 quedaron fuera porque usan otro formato (nombres de cuenta distintos y cuentas faltantes). Incorporarlos requiere adaptar la extracción y volver a entrenar el modelo, así que lo dejamos para la fase final del proyecto, una vez terminado el sistema completo.

### 5. Cómo se entrena, valida y prueba

- **Entrenamiento:** Random Forest (Breiman, 2001) con 542 empresas reales (4.211 empresa-año, 185 insolventes), con la proporción natural de insolventes y sin datos sintéticos.
- **Prueba:** 136 empresas reales que el modelo nunca vio (1.066 empresa-año, 51 insolventes).
- **Métricas:** Recall, Precisión, F1 y PR-AUC de la clase insolvente. El Accuracy no se usa como meta porque el 95 % de los casos son solventes.

Resultados en la prueba con empresas reales no vistas:

| F1 | Recall | Precisión | PR-AUC |
|---|---|---|---|
| **76,8 %** | **74,5 %** | 79,2 % | 85,8 % |

- Con las empresas micro, pequeñas y medianas de la prueba, el F1 sube a 94,4 % (con solo 18 casos insolventes, es una señal y no una cifra precisa).
- De las 3 quiebras legales, el modelo detecta 2. La tercera solo tiene datos hasta 2014, varios años antes de su quiebra.
- Entrenado con los datos sintéticos del Acta CreaEmpresas (proporciones 50/50 a 10/90), el F1 en la misma prueba real queda entre 71 % y 76 % y el PR-AUC baja a 80-82 %. Por eso no se usan.

---

## B. Proyecto

### 1. Alcance real

Un Producto Mínimo Viable web (SaaS) enfocado en estimar tempranamente el riesgo de insolvencia de una PYME. Incluye:

- Carga y validación de estados financieros (Excel o CSV).
- Motor predictivo de Machine Learning.
- Panel con semáforo de riesgo, las 3 variables que más elevan el riesgo, evolución en el tiempo, recomendaciones y exportación a PDF.
- Módulo de flujo de caja diario (ventas por método de pago, descuentos, retiros y cierre de caja), que alimenta la variable V7.

Quedan fuera: inventario, proveedores, cuentas por pagar, recursos humanos, punto de venta y facturación electrónica, que se mantienen en el ERP externo (Facto).

### 2. Componente de Machine Learning

Clasificador supervisado Random Forest que estima la probabilidad de que la empresa esté en zona de riesgo de insolvencia a partir de 7 variables:

| | Variable |
|---|---|
| V1 | Razón corriente |
| V2 | Capital de trabajo / activos totales |
| V3 | Leverage total |
| V4 | ROA operacional |
| V5 | Margen operacional |
| V6 | Rotación de activos |
| V7 | Volatilidad del flujo de caja diario (Ringeling, 2004) |

Se eligió Random Forest porque funciona bien con datos tabulares y permite explicar qué variables pesan en cada predicción. Se comparó con una Regresión Logística entrenada con los mismos datos reales: en la misma prueba, la Regresión Logística obtiene un F1 de 69,2 %, contra 76,8 % del Random Forest. Las redes neuronales quedan como trabajo futuro.

### 3. Fuentes de datos reales

Las del punto A.1: la CMF para entrenar y probar el modelo, el Boletín Concursal para el chequeo con quiebras legales, y Nstock Importaciones para probar el sistema con una PYME real.

### 4. Cómo se valida el modelo y qué otras empresas aportan datos

- **Validación estadística:** la prueba con 136 empresas reales no vistas (punto A.5). Proponemos como meta del requerimiento RNF-08 un **PR-AUC de al menos 80 % y un Recall y un F1 de la clase insolvente de al menos 70 %** en esa prueba; el modelo actual la cumple (PR-AUC 85,8 %, F1 76,8 %, Recall 74,5 %).
- **Validación financiera:** según lo acordado el 14-10-2026, la profesora Carolina San Martín revisará a mano los cálculos de una empresa real de la CMF y de las empresas con quiebra legal analizadas, para verificar que las cuentas contables estén bien clasificadas en las 7 variables.
- **Validación del sistema:** con los datos reales de Nstock Importaciones. Al ser una sola empresa sin quiebra, esta prueba verifica que el sistema funciona de punta a punta, pero no permite medir F1.

Otras empresas: por ahora no hay otra empresa comprometida a aportar datos. Algunas han mostrado interés, pero sin confirmación formal. Estamos gestionando con CreaEmpresas INACAP el contacto con otra empresa que pueda aportar sus datos reales para validar el sistema.

### 5. Cómo se mantienen los objetivos originales

El Machine Learning sigue siendo el centro del proyecto: la plataforma calcula una probabilidad de insolvencia para alertar antes de una crisis, no solo muestra datos históricos. La carga de datos y el módulo de caja existen para alimentar al modelo con datos limpios.

Estado de cada objetivo específico del acta de constitución aprobada:

| Objetivo del acta de constitución | Estado actual |
|---|---|
| Base de datos estructurada de datos financieros históricos, procesados y validados | Cumplido con la base de la CMF: 678 empresas chilenas, 5.277 empresa-año, procesadas con el mismo código de la plataforma |
| Identificación de los ratios más influyentes en el riesgo de quiebra | Se mantiene: 7 variables validadas por la profesora San Martín, con su ranking de importancia en el modelo |
| Modelo de Machine Learning entrenado y ajustado, incorporando el CAPM (Beta) | Se mantiene el modelo (Random Forest); el CAPM se retira (ver sección C) |
| Modelo evaluado con precisión, recall y F1, con precisión mínima de 80 % | Se mantiene la evaluación; el 80 % del acta se conserva como meta de PR-AUC (ver sección C) |
| Interfaz de visualización con nivel de riesgo y recomendaciones automáticas | Se mantiene: semáforo, variables que más elevan el riesgo, tendencia, recomendaciones y PDF |

El acta comprometía además validar el modelo comparando sus resultados con datos históricos de quiebras. Eso se cumple con la prueba de 136 empresas reales etiquetadas por zona de riesgo de Altman, más el chequeo con las 3 quiebras legales (punto A.5).

La adopción del ERP Facto por parte de Nstock no cambia los objetivos del proyecto. Solo cambia de dónde vienen algunos datos de entrada: la plantilla de carga acepta los estados financieros que exporta el ERP.

---

## C. Cambios respecto del proyecto aprobado (acta de constitución)

| Cambio | Justificación |
|---|---|
| **Meta del modelo:** el acta de constitución fijaba una precisión mínima de 80 % (el factor crítico de éxito la medía como accuracy). Se reemplaza por **PR-AUC ≥ 80 % y Recall y F1 de la clase insolvente ≥ 70 %** en la prueba con empresas reales no vistas (RNF-08) | Solo el 5 % de los casos son insolventes, así que un modelo que declare "solvente" a todas las empresas tendría 95 % de accuracy sin detectar ninguna insolvencia. El 80 % del acta se conserva en el PR-AUC, que mide qué tan bien el modelo ordena a las empresas de más a menos riesgo sin depender del umbral de decisión, y es la métrica recomendada para clases desbalanceadas (Saito y Rehmsmeier, 2015). Recall y F1 miden la detección de insolventes con el umbral del sistema; su meta de 70 % deja margen porque, con 51 casos insolventes en la prueba, cada caso mueve el F1 unos 2 puntos. El modelo actual cumple las tres: PR-AUC 85,8 %, F1 76,8 % y Recall 74,5 % (como referencia, accuracy 97,8 % y precisión 79,2 %). Las versiones intermedias del RNF-08 (90 % medido en datos sintéticos) también se reemplazan |
| Entrenamiento y prueba con datos reales de la CMF en lugar de datos sintéticos | El acta de constitución permitía validar con escenarios simulados, pero usted indicó que no son evidencia suficiente. Con datos reales el modelo rinde igual o mejor con empresas no vistas |
| Datos chilenos de la CMF en lugar del dataset de Taiwán | Datos del mercado chileno; el modelo de Taiwán llegaba a un F1 de 46,8 % |
| Se retira el CAPM (Beta) y el ajuste por riesgo de la industria | Mide la rentabilidad exigida por un inversionista, no la solvencia de la empresa (acordado con la profesora San Martín, 14-10-2026) |
| Se retira el contexto macroeconómico (RF-01, variable V8) | Los indicadores macro son iguales para todas las empresas de un mismo año, y Zurita (2008) muestra que su efecto sobre una empresa individual es pequeño. Los "indicadores económicos" del objetivo general quedan representados por los ratios financieros de la empresa |
| Se retiran RF-12 a RF-18 (inventario, proveedores, cuentas por pagar) | No estaban en el alcance del acta de constitución: se agregaron después y se retiran para volver a él. Ninguno alimenta al modelo predictivo |
| Se agrega el módulo de flujo de caja diario (RF-19 a RF-22) | No estaba en el acta. Calcula la volatilidad del flujo de caja (V7), que los estados financieros anuales no capturan (Ringeling, 2004). Es una entrada del modelo, no un reemplazo |

## D. Limitaciones

1. **La etiqueta es la zona de riesgo de Altman, no la quiebra legal**, porque solo 3 quiebras legales tienen estados financieros públicos.
2. **Las empresas de la CMF no son PYMEs típicas.** Las que son PYMEs por ventas incluyen holdings, inmobiliarias y empresas del Estado.
3. **V7 todavía no se calcula con datos reales**, porque el módulo de caja está en desarrollo. Mientras tanto se usa un valor neutro, y las cifras del punto A.5 se midieron así.
4. **La prueba tiene 51 casos insolventes**, así que las cifras tienen un margen de algunos puntos.

Quedamos atentos a sus comentarios.

Atentamente,

Ignacio Pozo Pozo y Arturo Quiroga Tello
Equipo Lostics, proyecto SmartFinanzas

---

**Referencias**

- Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. *The Journal of Finance, 23*(4), 589-609.
- Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5-32.
- Riquelme Garcés, V. (2018). *Evaluación de la capacidad de pronóstico de modelos predictivos de quiebra aplicados a empresas que cotizan en bolsa en Chile y Brasil* [Tesis de magíster]. Universidad del Bío-Bío.
- Ringeling Papić, E. A. (2004). *Análisis comparativo de modelos de predicción de quiebra y la probabilidad de bancarrota* [Seminario de título]. Universidad de Chile.
- Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE, 10*(3), e0118432.
- Zurita, F. (2008). *La predicción de la insolvencia de empresas chilenas* (Documento de Trabajo N.º 336). Pontificia Universidad Católica de Chile.
