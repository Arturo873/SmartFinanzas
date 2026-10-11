# Guía para redactar la metodología del modelo en el informe final

## Para qué sirve este documento

Es el **esqueleto con todo el contenido** que necesita el informe final para explicar el modelo predictivo v8: qué escribir en cada parte, con las cifras exactas, las fórmulas y las citas. No es el texto final: hay que redactarlo en lenguaje académico dentro del informe.

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

**Material de respaldo:** [fuentes_modelo_ml.md](fuentes_modelo_ml.md) (fuentes y páginas), [resultados_entrenamiento_v8.md](resultados_entrenamiento_v8.md) (detalle técnico) y [bitacora_modelo_v8.md](bitacora_modelo_v8.md) (decisiones con fecha).

---

## 1. Planteamiento del problema y enfoque

**Qué escribir:** por qué se necesita un modelo predictivo y por qué con datos sintéticos.

- La quiebra legal en Chile es un evento raro y tardío. Zurita (2008, p. 30) reporta una probabilidad promedio de quiebra de solo **0,64 %** en empresas chilenas.
- Al cruzar la CMF con el Boletín Concursal solo aparecen **3 empresas** con quiebra legal y estados financieros públicos. Con eso no se puede entrenar ningún modelo.
- **Decisión metodológica (Acta del 05-10-2026):** entrenar con datos sintéticos en múltiples proporciones y reservar los datos reales de Nstock para una validación posterior.
- **Enfoque de ciencia aplicada:** a diferencia de Excel o Power BI, que describen el pasado, el sistema **predice**.

## 2. Marco teórico: las 8 variables

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
| V8 Contexto macro | Variación del PIB, tasa UF, tipo de cambio real | Zurita (2008, pp. 7 y 29) | dirección del efecto |

**Puntos clave a desarrollar:**
- **V7 es el aporte propio del proyecto.** Ringeling dice que la volatilidad es "una importante variable omitida en los modelos de Altman (1968) y Ohlson (1980)". El proyecto la adapta desde la volatilidad de los activos (mercado) a la del flujo de caja de una PYME.
- **V8 viene de Zurita:** la probabilidad de quiebra baja con el crecimiento y sube con la tasa de interés y el tipo de cambio real. Hay que aclarar que su efecto individual es pequeño (+0,33 % ante un deterioro de una desviación estándar).
- **Beta CAPM (RF-01):** es distinto de V8. El Beta mide el riesgo del **sector** y se aplica después del modelo. V8 es el **contexto económico** y entra al modelo.

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

### 3.3 Borderline-SMOTE (Han et al., 2005)

- SMOTE crea casos nuevos interpolando entre un caso real y uno de sus vecinos: `x_nuevo = x_i + λ·(x_vecino − x_i)`, con λ entre 0 y 1.
- La variante *Borderline* solo usa los casos cercanos a la frontera entre clases, que son los más difíciles y los más informativos.

### 3.4 Reglas axiomáticas e identidad DuPont

- La interpolación lineal rompe una igualdad contable: `ROA = Margen × Rotación` (identidad DuPont). Por eso, en los casos sintéticos el ROA se recalcula con esa fórmula.
- Se descartan los casos sintéticos imposibles en la contabilidad. Por ejemplo: razón corriente > 1 si y solo si el capital de trabajo es positivo; en recesión no hay rentabilidades extremas. Se descartaron entre 367 y 486 casos por dataset.

## 4. Metodología de datos

**Qué escribir:** el flujo completo, idealmente con un diagrama.

1. **Fuente real:** 5.277 empresa-año de 678 empresas chilenas no financieras de la CMF (estados IFRS, balance a diciembre, 2012-2024).
2. **Contexto macro:** series oficiales del Banco Central de Chile (BDE), 2009-2026.
3. **Etiquetado:** insolvente si Z''EM < 1,10 o patrimonio ≤ 0. Resultan **236 casos (4,5 %)**.
4. **Separación antes de generar** (punto clave de rigor): el 20 % de las empresas se aparta **por empresa** para una prueba real que el modelo nunca ve. Así se evita la *fuga de datos* (*data leakage*), es decir, que el modelo sea evaluado con información que ya vio al entrenar.
5. **Generación:** 5 datasets de 10.000 filas en proporciones insolventes/solventes de 50/50, 40/60, 30/70, 20/80 y 10/90.
6. **V7 simulada:** `log(V7) = log(0,30) + 0,10·leverage + ruido`. La dirección (más deuda, más volatilidad) sigue a Ringeling (2004, p. 87); los parámetros son supuestos de diseño.

## 5. Resultados

**Qué escribir:** la tabla y su lectura.

| Proporción | Accuracy sint. | F1 sint. | F1 real | Recall real |
|---|---|---|---|---|
| **50/50 (elegido)** | **98,7 %** | **98,7 %** | **71,3 %** | 80,4 % |
| 40/60 | 99,1 % | 98,9 % | 70,2 % | 78,4 % |
| 30/70 | 98,7 % | 97,8 % | 68,9 % | 80,4 % |
| 20/80 | 98,6 % | 96,6 % | 70,2 % | 78,4 % |
| 10/90 | 98,0 % | 89,9 % | 75,9 % | 80,4 % |

- **Cumplimiento del Acta:** 4 de 5 proporciones superan el 90 %, y el modelo elegido supera el 95 % ideal.
- **Fluctuación por proporción** (lo que pide el Acta observar): con menos insolventes en el entrenamiento, el F1 sintético baja de 98,7 % a 89,9 %.
- **Criterio de elección:** el mejor F1 con empresas reales entre los que cumplen la meta.
- **Cifra en el sistema actual,** sin datos de caja: F1 de **69,7 %** con empresas reales.
- **Importancia de las variables:** el leverage es la más importante (31 %) y las variables macro pesan poco (≈ 6 % entre las tres), lo que coincide con Zurita.
- **Chequeo con quiebras legales reales:** el modelo detecta 2 de 3 (Sartor con 100 % y Telecom. Internacionales con 98 %). Son solo 3 casos, así que es evidencia cualitativa, no una métrica.

## 6. Discusión (lo más importante para la defensa)

Conviene adelantarse a las preguntas del profesor:

- **"¿Por qué 98,7 % y no la cifra real?"** Las dos se reportan. El 98,7 % mide al modelo con datos generados desde las mismas reglas, así que es optimista. El 69,7 % mide con empresas reales nunca vistas, y es la cifra honesta.
- **"¿No es circular etiquetar con Altman y después predecir?"** Sí, en parte, y se declara. El modelo aprende a reconocer la zona de riesgo de Altman a partir de 8 variables, de las cuales 4 no están en Z''EM. Sin quiebras reales suficientes, es la alternativa con respaldo bibliográfico.
- **"¿Por qué no comparar con el 46,8 % del modelo anterior?"** Porque miden cosas distintas: antes se medía contra quiebras legales de Taiwán y ahora contra la zona de riesgo de Altman en Chile.

## 7. Limitaciones y trabajo futuro

**Limitaciones:**
1. La etiqueta es la zona de riesgo de Altman, no la quiebra legal.
2. V7 es simulada, y el módulo de caja (RF-19 a RF-22) aún no existe.
3. Las empresas de la CMF son grandes, no PYMES como Nstock.
4. Los datos de la plantilla deben ser de los últimos 12 meses, porque el modelo se entrenó con estados anuales.
5. El Beta CAPM se aplica después del modelo.

**Trabajo futuro:**
1. Validación con los datos de Nstock (segunda etapa del Acta).
2. Implementar el módulo de caja para tener V7 real.
3. Migrar a redes neuronales (acuerdo del Acta).
4. Usar PYMES chilenas, por ejemplo los balances del MINVU (necesita OCR).

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
