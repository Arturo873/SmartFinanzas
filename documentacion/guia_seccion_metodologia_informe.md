# Guía para redactar la metodología del modelo en el informe final

## Para qué sirve este documento

Es el **esqueleto con todo el contenido** que necesita el informe final para explicar el modelo predictivo v11 (7 variables, entrenado solo con empresas reales de la CMF): qué escribir en cada parte, con las cifras exactas, las fórmulas y las citas. No es el texto final: hay que redactarlo en lenguaje académico dentro del informe.

También sirve para **preparar la defensa**: el Acta del 05-10-2026 exige "rigurosidad teórica con citas bibliográficas sólidas" y "dominio absoluto de los fundamentos matemáticos, las variables seleccionadas y la lógica de los algoritmos". Las secciones 3 y 6 cubren justo eso.

## Dónde va cada parte en el informe

RNF-08 indica que "los detalles metodológicos [...] se documentan en el **marco teórico** y en el **anexo de viabilidad técnica** del proyecto". Por eso:

| Sección de esta guía | Capítulo del informe |
|---|---|
| 1. Planteamiento del problema | Introducción / Justificación |
| 2. Marco teórico de las variables | **Marco teórico** |
| 3. Fundamentos matemáticos | **Marco teórico** (o Metodología) |
| 4. Metodología de datos | **Metodología** / Anexo de viabilidad técnica |
| 5. Resultados | **Anexo de viabilidad técnica** / Resultados |
| 6. Discusión | Resultados y discusión |
| 7. Limitaciones y trabajo futuro | Conclusiones |
| 8. Referencias | Bibliografía |

**Material de respaldo:** [fuentes_modelo_ml.md](fuentes_modelo_ml.md) (fuentes y páginas), [resultados_entrenamiento_v11.md](resultados_entrenamiento_v11.md) (detalle técnico) y [bitacora_modelo_v8.md](bitacora_modelo_v8.md) (decisiones con fecha).

---

## 1. Planteamiento del problema y enfoque

**Qué escribir:** por qué se necesita un modelo predictivo, qué se predice y con qué datos reales.

- La quiebra legal en Chile es un evento raro y tardío. Zurita (2008, p. 30) reporta una probabilidad promedio de quiebra de solo **0,64 %** en empresas chilenas.
- Al cruzar la CMF con el Boletín Concursal solo aparecen **3 empresas** con quiebra legal y estados financieros públicos. Con eso no se puede entrenar ningún modelo.
- **Por eso se predice la zona de riesgo de insolvencia de Altman (Z''EM), no la quiebra legal.** Con esa etiqueta hay **236 casos reales** en 678 empresas chilenas de la CMF, suficientes para entrenar.
- **Decisión metodológica:** entrenar y validar **solo con datos reales**. El Acta del 05-10-2026 proponía datos sintéticos en múltiples proporciones; se probaron y no mejoraron el resultado con empresas reales (sección 5), y el profesor del curso pidió que la evidencia sea con datos reales. Los datos de Nstock se reservan para validar el sistema con una PYME real.
- **Enfoque de ciencia aplicada:** a diferencia de Excel o Power BI, que describen el pasado, el sistema **predice**.

## 2. Marco teórico: las 7 variables

**Qué escribir:** una tabla con cada variable, su fórmula, qué mide y su fuente, más un párrafo por variable.

| Var. | Fórmula | Fuente | Umbral de riesgo |
|---|---|---|---|
| V1 Razón Corriente | AC / PC | Riquelme (2018, p. 105) | < 1 riesgo; < 0,5 riesgo alto |
| V2 Capital de Trabajo / AT | (AC − PC) / AT | Altman (1968) | < 0 |
| V3 Leverage | Pasivo / Patrimonio | Riquelme (2018, p. 106) | > 5 alto; patrimonio ≤ 0 = máximo |
| V4 ROA operacional | EBIT / AT | Altman (1968) | < 0 |
| V5 Margen Operacional | EBIT / Ingresos | Riquelme (2018, p. 107) | < 8 % alerta |
| V6 Rotación de Activos | Ingresos / AT | Altman (1968) | sin umbral en las fuentes |
| V7 Volatilidad del flujo | desv. est. del flujo diario / ingreso promedio diario | Ringeling (2004, p. 75) | sin umbral (aporte propio) |

**Puntos clave a desarrollar:**
- **V7 es el aporte propio del proyecto.** Ringeling dice que la volatilidad es "una importante variable omitida en los modelos de Altman (1968) y Ohlson (1980)". El proyecto la adapta desde la volatilidad de los activos (mercado) a la del flujo de caja de una PYME.
- **Cómo se elige el top 3 de RF-03:** no se usa la importancia global del Random Forest (es la misma para todas las empresas). Para cada empresa se calcula cuánto bajaría su probabilidad de insolvencia si una variable tomara el valor típico de una empresa solvente (mediana de las solventes de la CMF), dejando las demás iguales.
- **Sin CAPM:** el modelo no usa el Beta CAPM. En reunión con la profesora asesora Carolina San Martín (Área de Administración y Negocios) se acordó excluirlo, porque el CAPM entrega la **tasa de retorno exigida por un inversionista** y no es un ratio de solvencia.
- **Sin contexto macroeconómico:** una versión anterior tenía una V8 medida con 3 indicadores de Zurita (2008): variación del PIB, tasa de captación UF y tipo de cambio real. Se quitó para simplificar el modelo a 7 variables (Requerimientos v10). La misma fuente lo respalda: Zurita (2008, p. 29) muestra que el efecto macro sobre una empresa individual es pequeño (+0,33 % ante un deterioro de una desviación estándar), y en el modelo v8 esos 3 indicadores sumaban solo un 6 % de la importancia.

## 3. Fundamentos matemáticos

**Qué escribir:** las fórmulas y la lógica de cada técnica.

### 3.1 Z-score de Altman para mercados emergentes (Z''EM), usado para etiquetar

`Z''EM = 3,25 + 6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4`

- X1 = Capital de trabajo / AT
- X2 = Utilidades retenidas / AT
- X3 = EBIT / AT
- X4 = Patrimonio / Pasivo total
- Cortes: **< 1,10 zona de insolvencia**; 1,10-2,60 zona gris; > 2,60 zona segura (Riquelme, 2018, pp. 54-55).

**Justificación clave para la defensa:** el Z1 original de Altman marcaba al **40 %** de las empresas chilenas como insolventes, porque su variable X5 (ventas / activos) castiga a las empresas con activos grandes y poca rotación, como sociedades de inversión, eléctricas e inmobiliarias. Altman (2000) eliminó X5 justamente "para minimizar el efecto de la industria". Con Z''EM queda un **4,5 %** de insolventes.

### 3.2 Random Forest (Breiman, 2001)

- Conjunto de árboles de decisión, cada uno entrenado con una muestra aleatoria de los datos y de las variables. La predicción final es el voto promedio de los árboles.
- **Por qué no redes neuronales:** Grinsztajn et al. (2022) y Borisov et al. (2022) muestran que los modelos de árboles siguen superando al deep learning en datos tabulares de tamaño medio. Las redes neuronales quedan como trabajo futuro, como acordó el Acta.
- **Configuración:** 300 árboles, `min_samples_leaf = 2`, umbral de clasificación 0,5.

### 3.3 Métricas para clases desbalanceadas

- Solo el 4,8 % de la prueba es insolvente, así que un modelo que diga "solvente" a todas tendría 95 % de Accuracy sin detectar nada. Por eso se reportan las métricas de la **clase insolvente**:
  - **Recall** = insolventes detectados / insolventes reales.
  - **Precisión** = insolventes reales / empresas marcadas como insolventes.
  - **F1** = media armónica de Recall y Precisión: `2·P·R / (P + R)`.
  - **PR-AUC:** área bajo la curva Precisión-Recall; mide qué tan bien el modelo ordena a las empresas por riesgo, sin depender del umbral.

### 3.4 Comparación con datos sintéticos (Acta del 05-10-2026)

Solo como comparación; el modelo oficial no los usa.
- **Borderline-SMOTE** (Han et al., 2005) crea casos nuevos interpolando entre un caso real y uno de sus vecinos: `x_nuevo = x_i + λ·(x_vecino − x_i)`, con λ entre 0 y 1. La variante *Borderline* solo usa los casos cercanos a la frontera entre clases.
- La interpolación rompe la identidad DuPont (`ROA = Margen × Rotación`), así que en los sintéticos el ROA se recalcula. Se descartan los casos imposibles en la contabilidad (reglas axiomáticas del Miro): entre 54 y 152 por dataset.

## 4. Metodología de datos

**Qué escribir:** el flujo completo, idealmente con un diagrama.

1. **Fuente real:** 5.277 empresa-año de 678 empresas chilenas no financieras de la CMF (estados IFRS, balance a diciembre, 2012-2024).
2. **Etiquetado:** insolvente si Z''EM < 1,10 o patrimonio ≤ 0. Resultan **236 casos (4,5 %)**.
3. **Separación por empresa** (punto clave de rigor): el 20 % de las empresas (136, con 1.066 empresa-año y 51 insolventes) se aparta para una prueba real que el modelo nunca ve. Se separa **por empresa**, no por fila, para que los años de una misma empresa no queden a la vez en entrenamiento y prueba. Así se evita la *fuga de datos* (*data leakage*), es decir, que el modelo sea evaluado con información que ya vio al entrenar.
4. **Entrenamiento:** Random Forest con las 542 empresas restantes (4.211 empresa-año, 185 insolventes), con su proporción natural de insolventes y sin balanceo.
5. **V7 simulada:** `log(V7) = log(0,30) + 0,10·leverage + ruido`. La dirección (más deuda, más volatilidad) sigue a Ringeling (2004, p. 87); los parámetros son supuestos de diseño. En el sistema actual V7 toma un valor neutro (mediana de las solventes), porque el módulo de caja no existe todavía; la cifra principal se mide así.
6. **Comparación:** los 5 datasets sintéticos del Acta (50/50, 40/60, 30/70, 20/80 y 10/90) se entrenan con los mismos parámetros y se evalúan en la misma prueba real. Además, una Regresión Logística (Ohlson, 1980) se entrena con los mismos datos reales como modelo de contraste.
7. **Análisis por tamaño:** cada empresa-año se clasifica por ventas según la Ley 20.416 (micro, pequeña, mediana, grande) para medir el modelo por separado en empresas pequeñas y medianas.

## 5. Resultados

**Qué escribir:** las tablas y su lectura.

**Resultado principal** (136 empresas reales nunca vistas, sin datos de caja, como funciona hoy el sistema):

| Accuracy | F1 | Recall | Precisión | PR-AUC |
|---|---|---|---|---|
| 97,8 % | **76,8 %** | 74,5 % | 79,2 % | 85,8 % |

**Meta del RNF-08 v11:** PR-AUC ≥ 80 % y Recall y F1 de la clase insolvente ≥ 70 % en esta prueba. El modelo la cumple. El 80 % del acta de constitución se conserva en el PR-AUC; el accuracy se informa solo como referencia.

**Random Forest contra Regresión Logística** (mismos datos reales, misma prueba, sin datos de caja):

| Modelo | F1 | Recall | PR-AUC | Accuracy |
|---|---|---|---|---|
| **Random Forest (oficial)** | **76,8 %** | **74,5 %** | **85,8 %** | 97,8 % |
| Regresión Logística | 69,2 % | 70,6 % | 75,8 % | 97,0 % |

La Regresión Logística no alcanza la meta (F1 bajo 70 % y PR-AUC bajo 80 %), y el accuracy casi no distingue a los dos modelos.

**Datos reales contra sintéticos** (misma prueba real, V7 simulada):

| Entrenado con | F1 real | PR-AUC real | F1 en su prueba sintética |
|---|---|---|---|
| **Solo reales (oficial)** | 75,7 % | **85,5 %** | — |
| Sintético 50/50 | 76,2 % | 81,6 % | 98,4 % |
| Sintético 40/60 | 74,5 % | 79,5 % | 98,7 % |
| Sintético 30/70 | 75,5 % | 81,8 % | 98,1 % |
| Sintético 20/80 | 71,2 % | 80,7 % | 97,1 % |
| Sintético 10/90 | 72,0 % | 81,7 % | 92,7 % |

**Por tamaño** (prueba real, sin datos de caja):

| Se evalúa en | Entrenado con todas (oficial) | Entrenado solo con PYMEs |
|---|---|---|
| Prueba completa | **76,8 %** | 76,1 % |
| PYMEs por ventas (18 insolventes) | **94,4 %** | 91,9 % |
| Grandes (33 insolventes) | **66,7 %** | 65,5 % |

- **Los sintéticos no mejoran el resultado real:** el F1 queda igual (diferencias de 1-2 puntos son ruido con 51 insolventes) y el PR-AUC baja. La prueba sintética (92-99 %) es optimista, porque mide con datos generados desde las mismas empresas.
- **Fluctuación por proporción** (lo que pedía observar el Acta): con menos insolventes, el F1 sintético baja de 98,4 % a 92,7 %; el F1 real casi no cambia (71-76 %).
- **Por tamaño:** el modelo rinde mejor con las empresas pequeñas y medianas que con las grandes, y entrenar solo con PYMEs es peor que con todas.
- **Importancia de las variables:** el leverage es la más importante (32 %), seguida del capital de trabajo sobre activos (18 %) y el ROA operacional (15 %).
- **Chequeo con quiebras legales reales:** el modelo detecta 2 de 3 (Sartor con 98 % y Telecom. Internacionales con 92 %). Son solo 3 casos, así que es evidencia cualitativa, no una métrica.

## 6. Discusión (lo más importante para la defensa)

Conviene adelantarse a las preguntas del profesor:

- **"¿Por qué no usan datos sintéticos, si el Acta lo pedía?"** Se probaron en las 5 proporciones del Acta. Con empresas reales nunca vistas, el F1 queda igual y el PR-AUC baja, así que no aportan; y el 92-99 % que logran en su propia prueba es optimista, porque se mide con datos generados desde las mismas empresas.
- **"¿Las empresas de la CMF son PYMEs?"** No son PYMEs típicas, y se declara. Pero el 22 % de las empresa-año son micro, pequeñas o medianas por ventas, y en ellas el modelo rinde mejor que en las grandes (F1 94,4 % contra 66,7 %). Las 7 variables son razones financieras, así que no dependen de la escala en pesos. No existen balances públicos de PYMEs chilenas: el SII solo publica tramos de ventas y el Boletín Concursal no trae cifras.
- **"¿Por qué no entrenar solo con las PYMEs?"** Se probó: con solo 57 insolventes para aprender, rinde un poco peor en todos los conjuntos, incluso en las PYMEs.
- **"¿No es circular etiquetar con Altman y después predecir?"** Sí, en parte, y se declara. El modelo aprende a reconocer la zona de riesgo de Altman a partir de 7 variables, de las cuales 4 no están en Z''EM. Sin quiebras reales suficientes, es la alternativa con respaldo bibliográfico.
- **"¿Por qué no comparar con el 46,8 % del modelo anterior?"** Porque miden cosas distintas: antes se medía contra quiebras legales de Taiwán y ahora contra la zona de riesgo de Altman en Chile.
- **"¿Por qué no incluyen el contexto macroeconómico?"** Porque su efecto sobre una empresa individual es pequeño (Zurita, 2008, p. 29) y no mejoraba el modelo: con él, los 3 indicadores sumaban un 6 % de la importancia y el F1 con empresas reales sin datos de caja era menor (69,7 % contra 73,6 % sin él, ambos en la versión con sintéticos). Además, el sistema ya no depende de las series del Banco Central.
- **"¿Por qué no ajustan por sector con el CAPM?"** Porque el CAPM calcula la rentabilidad que exige un inversionista, no la capacidad de la empresa de pagar sus deudas. Así se acordó con la profesora asesora Carolina San Martín.

## 7. Limitaciones y trabajo futuro

**Limitaciones:**
1. La etiqueta es la zona de riesgo de Altman, no la quiebra legal.
2. V7 es simulada, y el módulo de caja (RF-19 a RF-22) aún no existe.
3. Las empresas de la CMF no son PYMEs típicas como Nstock; las PYMEs por ventas que hay entre ellas incluyen holdings, inmobiliarias y empresas del Estado.
4. La prueba tiene pocos insolventes (51, de ellos 18 PYME), así que las cifras tienen un margen de varios puntos.
5. Los datos de la plantilla deben ser de los últimos 12 meses, porque el modelo se entrenó con estados anuales.

**Trabajo futuro:**
1. Validación con los datos de Nstock (segunda etapa del Acta).
2. Implementar el módulo de caja para tener V7 real.
3. Migrar a redes neuronales (acuerdo del Acta).
4. Usar PYMES chilenas, por ejemplo los balances del MINVU (necesita OCR).
5. Recuperar los años 2009-2011 de la CMF, que hoy quedan fuera por diferencias en los nombres de las cuentas.

## 8. Referencias (APA 7)

- Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. *The Journal of Finance, 23*(4), 589-609. https://doi.org/10.1111/j.1540-6261.1968.tb00843.x
- Borisov, V., Leemann, T., Seßler, K., Haug, J., Pawelczyk, M., & Kasneci, G. (2022). Deep neural networks and tabular data: A survey. *IEEE Transactions on Neural Networks and Learning Systems*. https://doi.org/10.1109/TNNLS.2022.3229161
- Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5-32. https://doi.org/10.1023/A:1010933404324
- Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS 2022, Datasets and Benchmarks Track*. https://arxiv.org/abs/2207.08815
- Han, H., Wang, W.-Y., & Mao, B.-H. (2005). Borderline-SMOTE: A new over-sampling method in imbalanced data sets learning. En *Advances in Intelligent Computing (ICIC 2005)*, LNCS 3644 (pp. 878-887). Springer. https://doi.org/10.1007/11538059_91
- Ringeling Papić, E. A. (2004). *Análisis comparativo de modelos de predicción de quiebra y la probabilidad de bancarrota* [Seminario de título, Universidad de Chile]. https://repositorio.uchile.cl/handle/2250/108243
- Riquelme Garcés, V. (2018). *Evaluación de la capacidad de pronóstico de modelos predictivos de quiebra aplicados a empresas que cotizan en bolsa en Chile y Brasil* [Tesis de magíster, Universidad del Bío-Bío].
- Ríos Orrego, R., Quezada Rojas, K., & Tapia Valdés, A. (2018). Modelo predictivo de quiebra en empresas constructoras inscritas en el MINVU de Valparaíso. *Revista de Investigación Aplicada en Ciencias Empresariales, 7*(1), 29-38. https://doi.org/10.22370/riace.2018.7.1.1767
- Zurita, F. (2008). *La predicción de la insolvencia de empresas chilenas* (Documento de Trabajo N.º 336). Instituto de Economía, Pontificia Universidad Católica de Chile.

**Ojo:** dos citas (Altman et al., 2017, y Altman y Hotchkiss, 2006) solo las conocemos a través de Riquelme. En el informe deben citarse como "citado en Riquelme (2018)", porque no se leyeron los textos originales.
