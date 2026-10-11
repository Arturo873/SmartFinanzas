# Propuesta de Requerimientos v8 (modelo de 8 variables)

Fase 2 del plan "camino 3". Parte de **Requerimientos_funcionales_y_no_funcionales_v7.pdf**, del **Acta CreaEmpresas (05-10-2026)** y del tablero Miro "SmartFinanzas".
Las referencias R1-R10 corresponden a [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

## Resumen de cambios

| Req. | Cambio | Motivo |
|---|---|---|
| RF-01 | **Modificado** | Se suma el contexto macroeconómico (V8) al ajuste por sector |
| RF-03 | Ajuste menor | Explicabilidad sobre las 8 variables nuevas |
| RF-05 | Ajuste menor | Recomendaciones asociadas a cada grupo de variables |
| RF-08 | **Modificado** | La plantilla agrega EBIT, Ingresos Netos y Utilidades Retenidas |
| RF-09 | Ajuste menor | Validación de las columnas nuevas y cuadraturas contables |
| RF-10 | **Modificado** | La tabla muestra las 8 variables del modelo; la prueba ácida queda solo como referencia |
| RNF-05 | Ajuste menor | El motor procesa las 8 variables, no solo los ratios de liquidez |
| RNF-08 | **Reescrito** | Entrenamiento con datos sintéticos en varias proporciones y meta de 90-95 % (Acta) |
| RNF-09 | Ajuste menor | El módulo de datos macro también queda aislado |
| RNF-10 | **Modificado** | La caja pasa a alimentar al modelo (V7) |
| RF-02, RF-04, RF-06, RF-07, RF-11, RF-19 a RF-22, RNF-01 a RNF-04, RNF-06, RNF-07, RNF-11, RNF-12 | Sin cambios | No dependen de las variables del modelo |

---

## Las 8 variables del modelo (referencia para todos los requerimientos)

| Var. | Nombre | Fórmula | Fuente |
|---|---|---|---|
| V1 | Razón Corriente | Activo Corriente / Pasivo Corriente | R2, R3 |
| V2 | Capital de Trabajo sobre Activos | (Activo Corriente − Pasivo Corriente) / Activo Total | R1, R2 |
| V3 | Leverage Total | Pasivo Total / Patrimonio | R2 |
| V4 | ROA operacional | EBIT / Activo Total | R1, R2, R3 |
| V5 | Margen Operacional | EBIT / Ingresos Netos | R2 |
| V6 | Rotación de Activos | Ingresos Netos / Activo Total | R1, R3 |
| V7 | Volatilidad del Flujo de Caja | Desviación estándar del flujo de caja diario del período (ver RNF-10) | R3, R5 |
| V8 | Contexto Macroeconómico | Variación del PIB trimestral, tasa de interés y tipo de cambio real del período | R5 |

---

## Requerimientos funcionales modificados

### RF-01: Sector industrial y contexto macroeconómico

**Texto v7:** Como Dueño de la PYME, quiero seleccionar el sector industrial de mi empresa desde una lista desplegable, para que el sistema asigne automáticamente el coeficiente de mercado correspondiente al modelo CAPM [...].
*Validación v7:* El sistema debe listar al menos 5 sectores clave e impactar directamente el cálculo del score de riesgo macroeconómico.

**Historia de usuario v8:**
Como Dueño de la PYME, quiero seleccionar el sector industrial de mi empresa desde una lista desplegable, para que el sistema asigne automáticamente el coeficiente Beta del modelo CAPM (Capital Asset Pricing Model) correspondiente a ese sector y, además, considere el contexto macroeconómico chileno del período analizado (variación del PIB, tasa de interés y tipo de cambio real), de modo que el riesgo calculado refleje tanto el riesgo propio del sector como el riesgo sistémico de la economía.

**Validación v8:**
El sistema debe listar al menos 5 sectores clave y aplicar el Beta del sector seleccionado al score de riesgo. Además, debe obtener los indicadores macroeconómicos (V8) desde las series oficiales del Banco Central de Chile que correspondan al trimestre del período cargado. Si ese trimestre aún no está publicado, debe usar el último disponible e indicar en pantalla la fecha del dato utilizado.

**Fundamento:** Zurita (2008, R5, pp. 7 y 29) demuestra que la variación del PIB, la tasa de interés y el tipo de cambio real explican la tasa agregada de quiebras en Chile.

---

### RF-03: Panel de explicabilidad

**Historia de usuario v8:**
Como Dueño de la PYME, quiero ver un panel de explicabilidad que desglose las 3 variables financieras que más afectaron negativamente mi score, para comprender las razones del riesgo detectado por la IA sin necesidad de ser un experto técnico.

**Validación v8:**
Deben mostrarse textualmente, con un nombre comprensible para el usuario, las 3 variables (de las 8 del modelo) con mayor peso estadístico en la predicción, junto con su valor calculado.

---

### RF-05: Sugerencias financieras

**Validación v8** (se agrega la frase final):
Si el sistema arroja alerta Amarilla o Roja, debe desplegarse dinámicamente un bloque de recomendaciones financieras lógicas asociadas al tipo de riesgo detectado. **Cada recomendación debe corresponder al grupo de la variable que la origina: liquidez (V1, V2), endeudamiento (V3), rentabilidad (V4, V5), eficiencia (V6), estabilidad del flujo de caja (V7) o contexto económico (V8).**

---

### RF-08: Carga inicial con plantilla estandarizada

**Historia de usuario:** sin cambios.

**Validación v8:**
El sistema debe permitir arrastrar o seleccionar archivos .xlsx o .csv basados en la plantilla estandarizada, confirmar la lectura correcta del archivo y persistir los datos como base inicial del sistema. La plantilla debe contener, por empresa y período, las siguientes columnas:

| Columna | Estado | Usada en |
|---|---|---|
| Id_Empresa, Periodo | Existente | Identificación y cruce con V8 |
| Activo_Circulante, Pasivo_Circulante | Existente | V1, V2 |
| Activo_Total, Pasivo_Total | Existente | V2, V3, V4, V6 |
| Inventarios, Efectivo_Equivalentes, Utilidad_Neta | Existente | Tabla de referencia del Contador (RF-10) |
| **EBIT** (resultado operacional) | **Nueva** | V4, V5 |
| **Ingresos_Netos** | **Nueva** | V5, V6 |
| Patrimonio_Neto | Existente (ya se validaba Activo = Pasivo + Patrimonio) | V3 |
| **Utilidades_Retenidas** | **Nueva** | Z-score de Altman (Z1), usado para etiquetar los datos de entrenamiento (RNF-08) |

---

### RF-09: Validación del archivo de carga

**Validación v8** (se agrega la segunda oración):
Debe bloquearse el procesamiento si el archivo supera el umbral de tolerancia a nulos establecido, mostrando en pantalla los errores encontrados con su ubicación exacta. **También debe advertir los descuadres contables básicos: Activo Total distinto de Pasivo Total + Patrimonio (con una tolerancia de redondeo), Activo Corriente mayor que Activo Total o Pasivo Corriente mayor que Pasivo Total.**

---

### RF-10: Tabla resumen de ratios

**Texto v7 (validación):** Las fórmulas matemáticas aplicadas por el módulo ETL deben coincidir exactamente con la teoría financiera estándar (razón corriente, prueba ácida, endeudamiento, rentabilidad, etc.).

**Validación v8:**
La tabla debe mostrar las 8 variables que usa el modelo predictivo (V1 a V8), y sus fórmulas deben coincidir exactamente con la teoría financiera estándar y con las fuentes que las respaldan (Altman, 1968; Riquelme, 2018). Indicadores complementarios como la prueba ácida o la razón de caja pueden mostrarse como referencia para el Contador, identificados como "no utilizados por el modelo".

---

## Requerimientos no funcionales modificados

### RNF-05: Tiempo de respuesta del motor predictivo

**Validación v8:**
Una vez que el usuario presione el botón "Ejecutar Predicción", el motor de Machine Learning (Scikit-Learn) debe calcular las 8 variables del modelo, estimar la probabilidad de insolvencia y retornar el score numérico en un tiempo menor a 3 segundos.

---

### RNF-08: Calidad del modelo predictivo

**Texto v7 (validación):** El motor predictivo (Random Forest) entrenado y serializado debe ser evaluado mediante métricas robustas frente a clases desbalanceadas, aplicando Recall y F1-score sobre la clase minoritaria de insolvencia, descartando metas arbitrarias de Accuracy. [...]

**Historia de usuario:** sin cambios.

**Validación v8:**
El motor predictivo (Random Forest; Breiman, 2001) debe entrenarse desde cero con datasets sintéticos generados a partir de:
(a) la distribución de empresas chilenas reales informadas a la CMF, para la clase solvente;
(b) reglas axiomáticas de consistencia contable y los umbrales de la literatura, incluido el Z-score de Altman para empresas no cotizadas (Z1 < 1,23), para etiquetar la clase insolvente;
(c) sobremuestreo con Borderline-SMOTE (Han et al., 2005).

Se deben generar y evaluar al menos cinco datasets con distintas proporciones de empresas insolventes/solventes: 50/50, 40/60, 30/70, 20/80 y 10/90 (cada par suma 100 %). Para cada uno se deben reportar Accuracy, F1-score y Recall de la clase insolvente sobre un conjunto de prueba separado, no usado en el entrenamiento. El modelo seleccionado debe alcanzar como mínimo 90 % en Accuracy y F1-score, con 95 % como meta ideal.

Los datos reales de Nstock Importaciones se reservan para una etapa posterior de validación de inferencia, cuyos resultados se reportarán por separado. Los detalles metodológicos se documentan en el marco teórico y en el anexo de viabilidad técnica del proyecto.

**Fundamento:** Acta CreaEmpresas del 05-10-2026 (meta de 90-95 %, datos sintéticos en múltiples proporciones, Nstock solo para validación). Grinsztajn et al. (2022) y Borisov et al. (2022) respaldan mantener modelos de árboles para datos tabulares.

---

### RNF-09: Aislamiento modular

**Validación v8** (se agrega el texto en negrita):
El componente inteligente (scripts de Machine Learning, lógicas del coeficiente CAPM **y obtención de indicadores macroeconómicos del Banco Central**) debe estar aislado de la capa de presentación y del ORM de Django, permitiendo actualizar, recalibrar o reemplazar los modelos predictivos sin necesidad de reestructurar la base de datos MySQL ni modificar la interfaz de usuario.

---

### RNF-10: Integración caja → motor predictivo

**Historia de usuario v8:**
Como equipo de desarrollo, quiero que el módulo transaccional de caja alimente al motor predictivo con la volatilidad del flujo de caja diario (V7), sin conflictos de datos ni degradación del rendimiento operativo del sistema.

**Validación v8:**
El proceso ETL debe calcular V7 a partir de los cierres de caja diarios confirmados (RF-22) del período analizado, como la desviación estándar del flujo neto diario dividida por el ingreso promedio diario, para que sea comparable entre empresas de distinto tamaño. La sincronización debe ejecutarse de forma asincrónica o programada, sin bloquear las operaciones de registro del flujo diario y garantizando la consistencia de los datos. Si el período tiene menos de 20 cierres confirmados, el sistema debe usar un valor neutro para V7 e informarlo en la tabla de RF-10.

**Fundamento:** Ringeling (2004, R3, p. 75): "un aumento en la volatilidad incrementa la probabilidad de quiebra" y es "una importante variable omitida en los modelos de Altman (1968) y Ohlson (1980)".

---

## Puntos que el equipo debe revisar

1. ~~**V7 normalizada.**~~ **Aprobado (2026-10-11).** V7 = desviación estándar del flujo neto diario / ingreso promedio diario, para que sea comparable entre empresas de distinto tamaño. Es una decisión de diseño propia y se declara así en el informe.
2. **Mínimo de 20 cierres para V7.** Equivale a un mes hábil aproximado. También es una decisión de diseño; el equipo puede cambiar el número.
3. **La meta de 90-95 % se mide sobre datos sintéticos.** Como las etiquetas salen de reglas basadas en las mismas variables, el modelo puede alcanzarla con facilidad. Hay que declararlo en el informe y presentar la validación con Nstock como la prueba con datos reales. Si no, el profesor podría objetar que el modelo "se evalúa con sus propias reglas".
4. ~~**La proporción "80/100" del Acta.**~~ **Resuelto (2026-10-11).** Se interpreta como un error de tipeo de 20/80 (20 % insolventes, 80 % solventes). Las proporciones se escriben siempre como insolventes/solventes y cada par suma 100 %: 50/50, 40/60, 30/70, 20/80 y 10/90. Se agrega 10/90 porque es la más cercana a la realidad (Zurita, 2008, p. 30: la quiebra legal es un evento raro).
5. **El nombre de V8 en el Miro es "Riesgo Sistémico (Ajuste CAPM)".** En estricto rigor, CAPM es el Beta por sector y V8 es contexto macro (Zurita). Esta propuesta los mantiene separados dentro de RF-01 para no mezclar conceptos en la defensa.
