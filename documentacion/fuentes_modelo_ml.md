# Fuentes del modelo ML (7 variables)

Fase 1 del plan "camino 3". Cada dato indica de dónde sale y en qué página, para poder citarlo en el informe.
Fecha de revisión: 2026-10-11.

> **Actualización 2026-10-16 (Requerimientos v10):** el modelo pasó de 8 a 7 variables. Se quitó V8 (contexto macroeconómico) y ya no se usan las series del Banco Central. Lo que este documento dice de V8 se conserva como respaldo de esa decisión: Zurita (R5) muestra que el efecto macro sobre una empresa individual es pequeño (hallazgo 3).

## 1. Referencias verificadas (formato APA 7)

| # | Referencia | Enlace | Estado |
|---|---|---|---|
| R1 | Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. *The Journal of Finance, 23*(4), 589-609. | https://doi.org/10.1111/j.1540-6261.1968.tb00843.x | Verificada (DOI) |
| R2 | Riquelme Garcés, V. (2018). *Evaluación de la capacidad de pronóstico de modelos predictivos de quiebra aplicados a empresas que cotizan en bolsa en Chile y Brasil* [Tesis de magíster, Universidad del Bío-Bío]. | https://repositorio.ubiobio.cl/bitstreams/0e499388-def1-43ce-828a-632819e35b6d/download | Verificada y leída |
| R3 | Ringeling Papić, E. A. (2004). *Análisis comparativo de modelos de predicción de quiebra y la probabilidad de bancarrota* [Seminario de título de Ingeniero Comercial, Universidad de Chile]. Profesor guía: Rafael Romero Meza. | https://repositorio.uchile.cl/handle/2250/108243 | Verificada y leída (PDF en `DatasetSinteticoEntrenamientoML/ringeling_e.pdf`) |
| R4 | Ríos Orrego, R., Quezada Rojas, K., & Tapia Valdés, A. (2018). Modelo predictivo de quiebra en empresas constructoras inscritas en el MINVU de Valparaíso. *Revista de Investigación Aplicada en Ciencias Empresariales, 7*(1), 29-38. | https://doi.org/10.22370/riace.2018.7.1.1767 | Verificada y leída. **Ojo: el Miro dice 2017, la publicación es 2018** |
| R5 | Zurita, F. (2008). *La predicción de la insolvencia de empresas chilenas* (Documento de Trabajo N.º 336). Instituto de Economía, Pontificia Universidad Católica de Chile. | https://www.economia.uc.cl/docs/doctra/dt-336.pdf | Verificada y leída. Versión en inglés: *Economía Chilena, 11*(1), 93-116 |
| R6 | Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5-32. | https://doi.org/10.1023/A:1010933404324 | Verificada (DOI) |
| R7 | Han, H., Wang, W.-Y., & Mao, B.-H. (2005). Borderline-SMOTE: A new over-sampling method in imbalanced data sets learning. En *Advances in Intelligent Computing (ICIC 2005)*, LNCS 3644 (pp. 878-887). Springer. | https://doi.org/10.1007/11538059_91 | Verificada (DOI). No estaba en el Miro |
| R8 | Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS 2022, Datasets and Benchmarks Track*. | https://arxiv.org/abs/2207.08815 | Verificada |
| R9 | Borisov, V., Leemann, T., Seßler, K., Haug, J., Pawelczyk, M., & Kasneci, G. (2022). Deep neural networks and tabular data: A survey. *IEEE Transactions on Neural Networks and Learning Systems*. | https://doi.org/10.1109/TNNLS.2022.3229161 | Verificada (publicada en línea 2022; versión impresa 2024, vol. 35(6), 7499-7519) |
| R10 | Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep learning*. MIT Press. | https://www.deeplearningbook.org | Libro de referencia |

## 2. Respaldo y umbrales por variable

| Var. | Fórmula | Qué dicen las fuentes | Umbral de riesgo usable |
|---|---|---|---|
| V1 Razón Corriente | AC / PC | R2 p. 105: razón corriente < 1 indica pasivos de corto plazo mayores que activos de corto plazo; < 0,5 "baja capacidad de pago a corto plazo". R2 p. 116: insolvencia = "pasivo exigible mayor a su activo liquidable". | **< 1 riesgo; < 0,5 riesgo alto** |
| V2 Capital de Trabajo / AT | (AC − PC) / AT | Variable X1 del Z-score (R1; R2 p. 52-53). Por construcción, V2 < 0 ⇔ V1 < 1. | **< 0 riesgo** (consistente con V1) |
| V3 Leverage | Pasivo / Patrimonio | R2 p. 106: < 1 "buena capacidad de pago a sus acreedores"; > 5 lo califica como "bastante alto"; patrimonio negativo deja el indicador negativo. R2 p. 116: insolvencia cuando los pasivos superan a los activos. | **< 1 sano; > 5 riesgo alto; patrimonio ≤ 0 = riesgo máximo** |
| V4 ROA | EBIT / AT | Variable X3 del Z-score, la de mayor peso (R2 p. 52-53). R2 p. 106: ROA negativo = EBIT negativo, señal de deterioro. | **< 0 riesgo** |
| V5 Margen Operacional | EBIT / Ingresos | R2 p. 107: margen negativo por EBIT negativo; margen que "no supera el 8%" refleja "baja capacidad de la empresa para generar ingresos". | **< 0 riesgo; < 8 % alerta** |
| V6 Rotación de Activos | Ingresos / AT | Variable X5 del Z-score (R1). R4 p. 33-36: en PYMES constructoras los anticipos de clientes inflan este ratio y pueden ocultar la insolvencia. | **Sin umbral fijo en las fuentes**; se usa dentro del Z-score |
| V7 Volatilidad del flujo | Desv. estándar del flujo de caja diario | R3 p. 75: los modelos contables no capturan la volatilidad; "un aumento en la volatilidad incrementa la probabilidad de quiebra" y es "una importante variable omitida en los modelos de Altman (1968) y Ohlson (1980)". R3 p. 78: es el componente clave del modelo Black-Scholes-Merton. R3 p. 87 (Moody's): volatilidad de activos 21 % → prob. de quiebra 0,03 %; 39 % → 1,97 %. También R5 sección 2.1. | **Sin umbral contable en las fuentes.** Dirección confirmada: más volatilidad = más riesgo. Adaptar la volatilidad de activos (mercado) a la del flujo de caja es el aporte propio del proyecto |
| ~~V8 Contexto macro~~ (retirada en v10) | Variación PIB, tasa de interés | R5 p. 7 y 29: la variación del PIB, la tasa de interés y el **tipo de cambio real** explican la tasa agregada de quiebras. La probabilidad de quiebra baja con el crecimiento y sube con la tasa y el tipo de cambio. R5 p. 24: PIB trimestral a 4 trimestres; tasa de captación UF de 30 a 365 días. | Dirección del efecto; **efecto individual pequeño** (ver hallazgo 3) |

### Regla de etiquetado: Z-score de Altman para mercados emergentes (Z''EM)

R2 pp. 54-55: Altman (2000) eliminó X5 (Ventas / AT) del modelo para empresas no manufactureras, "para minimizar el efecto potencial de la industria"; Altman, Iwanicz-Drozdowska, Laitinen y Suvas (2017) agregaron la constante 3,25 para mercados emergentes:

`Z''EM = 3,25 + 6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4`

- X1 = Capital de trabajo / AT → **V2**
- X2 = Utilidades retenidas / AT → **no es variable del modelo** (columna `Utilidades_Retenidas` de la plantilla)
- X3 = EBIT / AT → **V4**
- X4 = Patrimonio libro / Pasivo total → **1 / V3**

Cortes: **Z''EM < 1,10 alta probabilidad de insolvencia**; 1,10-2,60 zona gris; > 2,60 sin problemas.

**Etiqueta usada (aprobada 2026-10-11):** insolvente si Z''EM < 1,10 **o** patrimonio ≤ 0 (pasivos mayores que activos; R2 p. 116).

**Por qué no Z1 (Altman y Hotchkiss, 2006, R2 pp. 53-54):** aplicado a 5.277 empresa-año reales de la CMF, Z1 < 1,23 marca al **40 %** como insolventes, porque su X5 castiga la baja rotación de activos (mediana 0,22 en las marcadas contra 0,62 en el resto) típica de sociedades de inversión, eléctricas e inmobiliarias. Z''EM marca al **4,5 %** y detecta en zona de insolvencia a 2 de las 3 empresas con quiebra real del Boletín Concursal (la tercera solo tiene datos hasta 2014).

## 3. Hallazgos importantes para el equipo

1. **La quiebra legal es muy rara en Chile.** R5 p. 30: la probabilidad promedio de quiebra en su muestra fue de solo 0,64 %. Esto confirma por qué no hay suficientes quiebras reales y por qué la etiqueta es la zona de riesgo de Altman (236 casos reales en la CMF), no la quiebra legal. *Desde el modelo v11 se entrena solo con esos casos reales, sin datos sintéticos.*
2. **Al Miro le falta una variable macro.** R5 usa tres variables: PIB, tasa de interés y **tipo de cambio real**. El Miro solo menciona PIB y tasa.
3. **El efecto macro es pequeño por empresa.** R5 p. 29: si todas las variables macro empeoran una desviación estándar, la probabilidad de quiebra de una empresa sube solo 0,33 %. V8 sirve como contexto, pero no va a decidir la predicción por sí sola. Conviene decirlo en el informe. *Confirmado al entrenar: en el modelo v8 los 3 indicadores sumaron un 6 % de la importancia; por eso V8 se retiró en los Requerimientos v10.*
4. **Faltan umbrales para V6 y V7.** Ninguna fuente da un valor de corte para ellas, y ninguna de las dos entra en la regla de etiquetado (Z''EM). V7 se simulará, lo cual se declara como limitación.
5. **Z''EM requiere utilidades retenidas.** Resuelto: se agregó la columna `Utilidades_Retenidas` a la plantilla (RF-08).
6. **Cita equivocada de V7 en la tabla de Reglas Axiomáticas del Miro** (revisado 2026-10-12). Esa tabla dice "Adaptación de Merton en Riquelme", mientras que la tabla de las 8 variables dice "Adaptación de Merton en Ringeling (2004)". La correcta es **Ringeling (R3)**: es quien desarrolla el modelo de Merton / Black-Scholes y la volatilidad como variable omitida (R3 pp. 75, 78 y 87). Riquelme (R2) solo lo menciona al resumir el trabajo de Ringeling (p. 17 del PDF: "un Modelo basado en la valoración de opciones de Merton y Black & Scholes") y no trabaja la volatilidad como predictor. En el informe se cita Ringeling (2004).

## 4. Fuentes de datos (del Miro, estado verificado)

| Fuente | Uso | Estado |
|---|---|---|
| CMF (FECU / IFRS) | Base real del entrenamiento | `DatasetSinteticoEntrenamientoML/cmf_empresas_reales.csv`: 5.277 empresa-año de 678 empresas (2012-2024), 236 insolventes según la regla Z''EM |
| Superir (Boletín Concursal) | Quiebras legales | Cruzado con la CMF por RUT: solo 3 empresas. Se usan como chequeo ilustrativo, no para entrenar |
| MINVU (Registro de Contratistas) | Balances de PYMES | No se usará por ahora (PDFs escaneados) |
| Banco Central de Chile | V8 (PIB, tasa, tipo de cambio) | **Ya no se usa** (V8 retirada en v10; el código que la descargaba se eliminó y queda en el historial de git, commit `e95d014`). Estaba disponible (2009-Q1 a 2026-Q3) desde las tablas públicas de la BDE, sin registro. Series: (1) "Indicadores macroeconómicos trimestrales, referencia 2018", fila *PIB, volumen (miles de millones $ encadenado)*, variación % respecto del mismo trimestre del año anterior; (2) "Tasas y flujo de captación promedio del sistema financiero, reajustables", fila *90 días a 1 año - tasa* (Zurita usa captación UF de 30 a 365 días; el BDE no publica el tramo UF de 30-89 días); (3) "Índice de tipo de cambio real - TCR (índice promedio 1986=100)" |
| ERP Facto / Nstock | V7 y validación final | Privada, para la validación posterior que pide el Acta |

## 5. Pendientes de esta fase

- [x] Tesis de Ringeling (R3) descargada y leída: confirma lo que el Miro le atribuye sobre la volatilidad (V7).
- [x] Tipo de cambio real agregado a V8 (hallazgo 2).
- [x] X2 resuelto con la columna `Utilidades_Retenidas`; etiquetado con Z''EM en vez de Z1.
- [x] Series del Banco Central descargadas sin registro (tablas públicas de la BDE).
