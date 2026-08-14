# Búsqueda de mejora de F1 del motor predictivo — registro de evidencia

Este documento consolida los intentos realizados para acercar el F1-score del
modelo predictivo (`entrenar_modelo_oficial.py`) al 80% exigido por el RNF-08,
y sirve de respaldo ante el profesor guía si la meta no se alcanza. Reemplaza
al prompt de Colab usado originalmente (`prompt_colab_mejorar_f1.md`), cuyo
contenido queda preservado e integrado aquí.

## Restricción de diseño (no negociable)

El modelo solo puede usar ratios calculables desde la plantilla de carga
Excel/CSV ya aprobada como requerimiento funcional (RF-08). Cambiar la
plantilla implicaría rediseñar un RF ya validado, así que no se considera.

```
razon_corriente                 = activo_circulante / pasivo_circulante
prueba_acida                    = (activo_circulante - inventario) / pasivo_circulante
endeudamiento_corto_plazo       = pasivo_circulante / pasivo_total
solvencia_general               = activo_total / pasivo_total
cobertura_operacional           = utilidad_neta / pasivo_circulante
rentabilidad_activos            = utilidad_neta / activo_total
capital_trabajo_sobre_activos   = (activo_circulante - pasivo_circulante) / activo_total
```

La etiqueta objetivo (`Bankrupt`) tiene que ser un resultado histórico real de
quiebra, no una fórmula de reglas inventada (ya se cometió ese error una vez:
etiquetar con un score sintético hace que accuracy/F1 midan si el modelo
imita la fórmula, no si predice insolvencia real).

## Dataset base

**Taiwanese Bankruptcy Prediction** (UCI ML Repo #572 / Kaggle), 6,819
empresas, 220 quiebras (3.2%), columnas ya normalizadas 0-1 salvo
`Current Ratio` y `Quick Ratio` (outliers extremos, recortados con
`.clip(upper=10)` antes de escalar).

## Intento 1 — Iteración en Colab sobre el mismo dataset (histórico)

| Intento | AUC | F1 (umbral óptimo) | Accuracy | Recall |
|---|---|---|---|---|
| RandomForest, 5 ratios, class_weight='balanced' | 0.89 | 36.4% | 90.7% | 68% |
| + 2 ratios más (rentabilidad_activos, capital_trabajo_sobre_activos) | 0.925 | 48.4% | 95.3% | 68% |
| + SMOTE sobre el train set | 0.915 | 45.6% | 95.5% | 59% |
| + las 95 columnas originales de Taiwan (en vez de solo 7 ratios) | 0.938 | 48.6% | 95.8% | 61% |
| Combinar Taiwan + Polish Companies Bankruptcy (UCI #365, mapeando a los mismos 7 ratios) | 0.76 | 21.2% | 87.1% | 38% |

**Conclusiones:**
- El techo de F1 (~48%) no lo pone la cantidad de columnas (95 columnas dio
  casi lo mismo que 7) ni la cantidad de filas (6,819 es suficiente). El
  cuello de botella es el **desbalance de clases** (solo 3.2% quiebras).
- SMOTE (sobremuestreo sintético) casi no cambió nada.
- Combinar datasets de países/épocas distintos **empeoró** el resultado
  (probablemente por diferencias de distribución entre economías/normas
  contables): F1 cayó de 48% a 21.2%. Mezclar fuentes sin verificar
  compatibilidad de distribuciones no es una solución por sí sola.

## Intento 2 — Aplicado a producción (`entrenar_modelo_oficial.py`)

De la tabla anterior, se integraron al script real las dos técnicas de menor
riesgo y mayor impacto (agregar los 2 ratios + optimizar el umbral de
decisión vía validación cruzada de 5 folds, en vez del umbral fijo 0.5):

| Métrica | Antes | Después |
|---|---|---|
| Accuracy | 90.7% | 95.2% |
| Recall | 68.2% | 65.9% |
| F1-Score (test) | 32.1% | **46.8%** |
| F1-Score (cross-validation en train) | — | 41.7% |
| Umbral de decisión | 0.5 (por defecto) | 0.68 (optimizado) |

El F1 de test (46.8%) es cercano al de CV (41.7%), lo que indica que la
mejora es real y no un sobreajuste al split de prueba.

## Intento 3 — Búsqueda de datasets adicionales fuera de Kaggle

Se catalogaron alternativas usando un survey académico (arXiv 2411.01928,
"Datasets for Advanced Bankruptcy Prediction: A survey and Taxonomy"):

| Dataset | País | Empresas | % Quiebra | Tipo | Viable |
|---|---|---|---|---|---|
| Taiwanese (en uso) | Taiwán | 6,819 | 3.2% | Mixto | Sí (ya integrado) |
| Polish | Polonia | 7,027-9,792 | 3.9-6.9% | PYME | Ya probado, empeoró al combinar |
| American | EE.UU. | 8,262 | 6.6% | Públicas grandes | No probado |
| Russian | Rusia | 2,457 | 18.6% | PYME | **No viable por ahora** — columnas sin nombre (`L1-L4`, `T1-T4`, `S1-S15`...), sin diccionario de datos en el repo; requeriría leer el paper original (Zelenkov et al. 2017) para mapear cada código a un ratio real antes de poder usarlo |
| HAT | China | 13,489 | 26.4% | PYME | **Descartado** — no son ratios financieros, son archivos de grafo (relaciones societarias/directorios en `.npy`/`.pkl`), incompatible con una arquitectura de balance contable simple |
| SMEsD | China | 3,976 | No documentado | PYME | No explorado en detalle |
| Slovak (Data Mendeley) | Eslovaquia | 21,272 | Alto desbalance también | PYME | No explorado en detalle |

**Búsqueda específica de datos chilenos/latinoamericanos:** no se encontró
ningún dataset público con datos reales de quiebra a nivel de empresa (se
revisó SII, CORFO, INE, awesome-data-chile, y bases académicas del BID). Lo
más cercano es una base del BID sobre deuda corporativa 1990-2002 (sin
etiqueta de quiebra) y bases comerciales cerradas (ej. Osiris). Esto
confirma el riesgo "Falta de Datos" ya identificado en el plan de proyecto
(sección 4.1.5): no es falta de búsqueda, es que la fuente no existe
abierta para el contexto chileno/PYME.

## Intento 4 — Integración a producción: ajuste CAPM y desajuste de escala

Al conectar `modelo_riesgo.joblib` a `AppWeb/views.py` (`ejecutar_prediccion`),
surgieron dos hallazgos adicionales, documentados aquí porque afectan cómo se
interpreta el score que ve el usuario final, aunque no cambian el F1 medido
sobre el dataset de Taiwan (46.8%, intacto).

### Ajuste CAPM (Beta de industria)

El dataset de Taiwan no trae columna de industria/sector, por lo que no hay
datos históricos reales que respalden entrenar el modelo con un "Beta" como
feature más (hacerlo habría significado fabricar una columna, repitiendo el
error de etiquetas sintéticas que ya se evitó). En su lugar, el Beta del
sector se aplica **después** de la predicción, como un ponderador sobre la
probabilidad de quiebra que entrega el modelo (`ajustar_riesgo_por_capm` en
`AppWeb/viewsML.py`):

```
probabilidad_ajustada = probabilidad_base × (1 + (beta_sector - 1) × 0.5)
```

Beta = 1.0 (riesgo de mercado promedio) no cambia el score; sectores más
volátiles (ej. Tecnología, beta=1.20) lo suben; sectores más estables (ej.
Telecomunicaciones, beta=0.75) lo bajan. Es un overlay moderado (±10-12.5%
relativo con los betas reales del sistema, que van de 0.75 a 1.20), no un
factor que domine sobre el resultado del modelo. Esto cumple el alcance del
producto ("aplicará el modelo CAPM para ajustar la predicción") sin
comprometer la validez del F1 medido, que sigue midiéndose solo sobre los
ratios financieros reales.

### Desajuste de escala en 3 de los 7 ratios

3 columnas de Taiwan (`Operating Funds to Liability`, `Net Income to Total
Assets`, `Working Capital to Total Assets` → `cobertura_operacional`,
`rentabilidad_activos`, `capital_trabajo_sobre_activos`) vienen
pre-normalizadas 0-1 por los autores originales del dataset con una fórmula
no documentada. La mediana de `rentabilidad_activos` es 0.81 con desviación
estándar de solo 0.04 — hasta las empresas que sí quebraron tienen mediana
0.77, es decir, toda la variación real vive comprimida en un rango angosto
cerca de 1, no en la escala 0-1 completa.

Los ratios crudos que calcula Django (ej. `utilidad_neta / activo_total` de
una empresa real con pérdidas, que da negativo) caen muy por fuera de ese
rango angosto si se pasan sin ajustar, y el árbol los enruta a hojas poco
pobladas que no reflejan quiebra real — el score subestima el riesgo de
empresas en pérdidas.

**Corrección aplicada:** `_calibrar_a_escala_taiwan()` en `viewsML.py`
reescala esos 3 ratios crudos con una interpolación lineal por tramos,
usando como anclas la mediana de empresas sanas, la mediana de empresas
quebradas y el percentil 25 de empresas quebradas del propio dataset de
Taiwan (no constantes inventadas). Es una aproximación heurística —no existe
forma de invertir exactamente la normalización original de Taiwan, porque
los autores no publicaron la fórmula— pero corrige la dirección del score:
en pruebas con empresas sintéticas (sana / con pérdidas / patrimonio
negativo), el score pasó de subestimar sistemáticamente el riesgo a
ordenar correctamente sana (11.5) < riesgosa (27.4) < crítica (33.1).

**Límite que queda sin resolver:** el modelo, validado in-sample contra las
220 empresas que sí quebraron en Taiwan, predice una probabilidad mediana de
93% quiebras reales — el modelo en sí es sólido dentro del rango que vio en
entrenamiento. Pero un RandomForest **no extrapola probabilidad más allá del
caso más extremo que observó en entrenamiento** (limitación estructural del
algoritmo, no del código): un caso más severo que el peor que vio Taiwan cae
en la misma hoja de decisión que ese peor caso, sin bajar más. Como el
dataset de Taiwan son empresas públicas grandes, nunca observó un caso con
patrimonio muy negativo combinado con pérdidas severas simultáneas, así que
una PYME real en esa situación extrema podría no llegar a alerta Roja pese a
estar en insolvencia real. Alternativas para resolverlo (no implementadas
por ahora): un modelo que sí extrapola linealmente (ej. regresión logística)
en paralelo, o repesar el ensamble hacia el extremo cuando varias señales
coinciden en el peor cuartil observado.

## Intento 5 — Balanceo del train set (undersampling / SMOTE / SMOTEENN)

Sugerencia externa (ChatGPT) a evaluar: en vez de solo `class_weight='balanced'`,
balancear explícitamente el train set (undersampling a 1:1, SMOTE, SMOTEENN),
manteniendo el test set intacto con la distribución original para evitar data
leakage. Se implementó en `experimento_balanceo.py`, reutilizando el mismo
split 80/20 (`random_state=42`) que el modelo oficial para que la comparación
sea directa.

| Experimento | Filas train | F1 test (real) | F1 CV-train | Precisión | Recall |
|---|---|---|---|---|---|
| Baseline (`class_weight='balanced'`, producción actual) | 5,455 | **46.8%** | 41.7% | 36.2% | 65.9% |
| Undersampling 1:1 (220/220) | 352 | 31.3% | 85.6% | 19.7% | 77.3% |
| Undersampling 1:4 (220/~880) | 880 | 35.5% | 75.3% | 23.2% | 75.0% |
| SMOTE 1:1 | 10,558 | 34.4% | 93.9% | 22.3% | 75.0% |
| SMOTEENN | 9,689 | 34.5% | 96.8% | 22.2% | 77.3% |

**Conclusión: el balanceo del train set empeoró el F1 real, no lo mejoró.**
El baseline actual sigue siendo la mejor configuración encontrada.

Lo más relevante es la brecha entre `F1 CV-train` (75-97% con las técnicas de
balanceo) y `F1 test` (31-35%, evaluado sobre el test set real e intacto). Esa
brecha es precisamente el riesgo de "F1 artificialmente alto" que se buscaba
evitar: balancear el train hace que el CV interno (medido sobre datos ya
balanceados/sintéticos) luzca excelente, pero no se traduce a las empresas
reales del test set. Todas las variantes de balanceo suben el recall
(75-77% vs 65.9% del baseline) a costa de hundir la precisión (19-23% vs
36.2%), y el F1 combina ambos — el resultado neto es peor.

Esto refuerza, con un experimento adicional y limpio (sin data leakage), la
conclusión ya alcanzada en el Intento 1 con SMOTE: el cuello de botella no es
la falta de una técnica de rebalanceo específica por probar, es el
desbalance estructural de la clase minoritaria en el dataset disponible.

## Intento 6 — Combinar Taiwan + Polish, re-hecho con mapeo cuidadoso

El Intento 1 (fila 5) reportó que combinar Taiwan + Polish hundía el F1 de
48% a 21.2%, hecho originalmente en Colab. Se rehizo el experimento en este
repo (`experimento_combinar_polish.py`), usando el dataset Polish crudo
(`polish_raw/*.arff`, UCI #365, 5 horizontes de 1-5 años, 43,265 filas
válidas tras limpiar división-por-cero/NaN, 4.8% quiebras) mapeado a los
mismos 7 ratios vía la definición pública de atributos del dataset
(`Attr4`, `Attr46`, `Attr51/Attr2`, `Attr17`, `Attr1/Attr51`, `Attr1`,
`Attr3`), agregando las filas Polish **solo al train set de Taiwan**
(split 80/20 hecho antes de tocar Polish, para que el test set sea 100%
Taiwan intacto y comparable con el baseline):

| Experimento | Filas train | F1 test | Precisión | Recall |
|---|---|---|---|---|
| Baseline (solo Taiwan) | 5,455 | 44.3% | 32.3% | 70.5% |
| Taiwan train + Polish combinado | 48,720 | 43.7% | 34.7% | 59.1% |

**Resultado: combinar es prácticamente neutro (44.3% → 43.7%), no catastrófico.**
Esto **contradice** el resultado de 21.2% registrado en el Intento 1 — la
diferencia más probable es que el mapeo de ratios hecho en Colab haya sido
menos cuidadoso (ej. usar columnas Polish sin dividir correctamente para
obtener el mismo ratio, o no aislar el test set). Se mantiene este resultado
más reciente como el válido, por estar hecho con el test set aislado y el
mapeo documentado arriba. De cualquier forma, ni el resultado nuevo (43.7%)
ni el antiguo (21.2%) acercan el F1 al 80% requerido — combinar datasets de
países distintos no es una vía para cerrar la brecha.

Se probó además balancear el train combinado (mismo test set de Taiwan
intacto), por si el desbalance seguía dominando incluso con más datos:

| Experimento | F1 test | Precisión | Recall | F1 CV-train |
|---|---|---|---|---|
| Taiwan+Polish combinado (sin balancear) | 43.7% | 34.7% | 59.1% | 23.4% |
| + undersampling 1:1 | 23.0% | 13.3% | 86.4% | 73.5% |
| + SMOTE 1:1 | 31.9% | 20.1% | 77.3% | 76.5% |
| + SMOTEENN | 35.1% | 22.7% | 77.3% | 82.5% |

Mismo patrón que el Intento 5: balancear (aun con 48,720 filas de train)
empeora el F1 real (23-35% vs 43.7% sin balancear), a pesar de que el F1
de CV en train luce mucho mejor (73-83%) — la misma trampa de F1
artificialmente inflado, ahora confirmada también con el dataset combinado
y con casi 10x más datos de entrenamiento. El desbalance de clases sigue
siendo el techo, no la cantidad de filas.

## Intento 7 — Dataset American (Lombardo et al. 2022), combinado y balanceado

Se probó el dataset "American Bankruptcy" (Kaggle "US Company Bankruptcy
Prediction", 78,682 filas, 8,262 empresas NYSE/NASDAQ 1999-2018, 6.63%
quiebras — la mejor proporción de clases de todos los datasets evaluados
hasta ahora). Contiene cifras crudas en dólares (no ratios pre-normalizados
como Taiwan/Polish), lo que en teoría permite calcular los 7 ratios con la
fórmula exacta.

**Hallazgo metodológico importante:** el mirror de GitHub de este dataset
(`sowide/bankruptcy_dataset`) tiene las columnas `X1`-`X18` **reordenadas**
respecto al orden oficial del paper (Lombardo et al., *Future Internet*
2022, Table 2). Usar ese CSV sin darse cuenta produce ratios sin sentido
(Activo Total < Activo Circulante en 72% de las filas; `Total Current
Liabilities` idéntica a `Total Liabilities` en el 100% de las filas — ambos
síntomas de columnas mal alineadas, no de datos corruptos). Se verificó
descargando el CSV oficial de Kaggle (`US Company Bankruptcy Prediction/
american_bankruptcy.csv`) y confirmando el orden correcto contra
identidades contables (`Gross Profit = Net Sales − COGS` exacto, `EBIT =
EBITDA − D&A` exacto, `Total Assets ≥ Current Assets` en 99.99% de filas).
**Cualquier uso futuro de este dataset debe partir del CSV de Kaggle, no
del mirror de GitHub.**

Mapeo usado (orden oficial, confirmado): `razon_corriente=X1/X14`,
`prueba_acida=(X1-X5)/X14`, `endeudamiento_corto_plazo=X14/X17`,
`solvencia_general=X10/X17`, `cobertura_operacional=X6/X14`,
`rentabilidad_activos=X6/X10`, `capital_trabajo_sobre_activos=(X1-X14)/X10`.

| Experimento | F1 test | Precisión | Recall |
|---|---|---|---|
| Baseline (solo Taiwan) | 46.8% | 36.2% | 65.9% |
| Taiwan train + American combinados | 44.1% | 33.7% | 63.6% |
| + undersampling 1:1 | 26.7% | 15.9% | 84.1% |
| + SMOTE 1:1 | 34.9% | 22.5% | 77.3% |
| + SMOTEENN | 34.7% | 22.4% | 77.3% |
| **Solo American (train/test propios, sin Taiwan)** | **21.6%** | 14.6% | 41.5% |

**Conclusión: combinar no ayuda (44.1% vs 46.8%), y American evaluado solo
da un F1 nativo aún más bajo (21.6%) que Taiwan solo**, a pesar de tener
mejor proporción de clases (6.6% vs 3.2%). La causa más probable es que los
7 ratios calculados desde cifras crudas en dólares de empresas de tamaños
muy dispares (desde microcaps hasta grandes NYSE) introducen más ruido de
escala que las columnas ya normalizadas de Taiwan — el mismo problema de
"desajuste de escala" ya documentado en el Intento 4, ahora confirmado
también como causa de bajo desempeño en un dataset completo, no solo en la
integración a producción. Balancear el combinado repite el mismo patrón de
los Intentos 5 y 6: sube el recall, hunde la precisión, empeora el F1 neto.

## Intento 8 — Literatura académica y Gradient Boosting

Se buscó en literatura académica reciente (2025-2026) qué F1 logran otros
trabajos en el mismo problema exacto, para saber si el techo encontrado
(~44-48%) es un problema de nuestra metodología o un límite conocido del
problema en sí:

- Un paper con metodología rigurosa (train/test separado antes de
  balancear, igual que aquí) usando **el mismo dataset Taiwanese** (6,819
  empresas, 3.2% quiebras) **ni siquiera reporta F1 como métrica
  principal** — usa F2, PR-AUC y costo esperado, señalando explícitamente
  que el F1 es una métrica poco informativa bajo desbalance tan extremo.
- Un survey comparativo de métodos de aprendizaje desbalanceado en
  datasets con 3-7% de clase minoritaria (mismo rango que Taiwan/Polish)
  reporta como mejor resultado un F1 estimado de **30-50%** — coincide con
  nuestro 44-48%.

Esto respalda que **80% de F1 no es una meta realista para este tipo de
problema con datos públicos disponibles**, no solo para esta
implementación puntual.

El primer paper reportó que Gradient Boosting (XGBoost/HistGradientBoosting)
superaba a Random Forest, así que se probó (`experimento_boosting.py`,
mismo split y mismo umbral óptimo por CV que el modelo oficial):

| Modelo | F1 test | Precisión | Recall |
|---|---|---|---|
| RandomForest class_weight='balanced' (producción actual) | **46.8%** | 36.2% | 65.9% |
| HistGradientBoosting class_weight='balanced' | 40.0% | 32.4% | 52.3% |
| XGBoost con scale_pos_weight=30 | 41.8% | 31.1% | 63.6% |
| XGBoost sin ajuste de peso | 46.3% | 39.1% | 56.8% |

**El Random Forest actual sigue siendo la mejor configuración.** A
diferencia del paper (que trabaja con más features/variantes), con solo 7
ratios y 6,819 filas el boosting no superó al Random Forest — con pocos
datos y pocas variables, RF con `class_weight='balanced'` generaliza mejor
que el boosting, que tiende a sobreajustar más rápido en ese régimen.

## Intento 9 — BalancedRandomForest y EasyEnsemble (mejora real encontrada)

A diferencia de XGBoost/HistGradientBoosting (Intento 8), se probaron dos
métodos que el survey académico ranqueó primero para este tipo de problema:
`BalancedRandomForestClassifier` (cada árbol del bosque se entrena sobre un
bootstrap balanceado, undersampling interno por árbol) y
`EasyEnsembleClassifier` (varios AdaBoost, cada uno entrenado sobre un
subconjunto distinto de la clase mayoritaria igualado en tamaño a la clase
minoritaria, combinados por voto) — ambos de `imbalanced-learn`, distintos
de solo usar `class_weight='balanced'` como hace el modelo actual. Mismo
dataset, split, umbral óptimo por CV (`experimento_balanced_ensembles.py`).

También se midió F2-score (le da más peso al recall que a la precisión) y
PR-AUC, ya que la literatura revisada en el Intento 8 usa esas métricas en
vez de F1 puro para este tipo de problema.

| Modelo | Umbral optimizado para | F1 | Precisión | Recall | PR-AUC |
|---|---|---|---|---|---|
| RandomForest class_weight='balanced' (producción actual) | F1 | 46.8% | 36.2% | 65.9% | 43.3% |
| RandomForest (mismo modelo, umbral optimizado para F2) | F2 | 39.5% | 27.1% | 72.7% | 43.3% |
| BalancedRandomForest | F1 | 43.4% | 32.9% | 63.6% | 39.1% |
| BalancedRandomForest | F2 | 40.5% | 28.1% | 72.7% | 39.1% |
| **EasyEnsemble** | F1 | **49.5%** | 41.5% | 61.4% | 43.5% |
| EasyEnsemble | F2 | 40.3% | 27.8% | 72.7% | 43.5% |

**Hallazgo positivo (el único de toda la búsqueda): EasyEnsemble con umbral
optimizado para F1 sube el F1 real de 46.8% a 49.5%**, con mejor precisión
(41.5% vs 36.2%) y recall similar (61.4% vs 65.9%). El PR-AUC es
prácticamente igual entre RandomForest y EasyEnsemble (43.3% vs 43.5%) —
ambos ordenan el riesgo casi igual de bien; la diferencia de F1 viene de
que el comité de AdaBoost sobre submuestras balanceadas da probabilidades
mejor calibradas en el punto de corte elegido, no de que "vea" mejor los
datos. BalancedRandomForest, en cambio, quedó peor que el baseline (43.4%).

Optimizar el umbral para F2 en vez de F1 sube el recall a ~72-73% en los
tres modelos, pero hunde la precisión y el F1 — confirma que F1 y F2
empujan en direcciones opuestas, como señalaba la literatura del Intento 8.

**Estado: documentado, no aplicado a producción.** Sigue sin acercarse al
80% del RNF-08, pero es una mejora real y reproducible (49.5% vs 46.8%)
sobre `entrenar_modelo_oficial.py`. Pendiente de decisión del equipo sobre
si vale la pena reemplazar `RandomForestClassifier` por
`EasyEnsembleClassifier` en el modelo oficial.

## Conclusión general

Con datos de balance financiero simple (5-7 ratios, sin variables
macroeconómicas, texto o series temporales largas), el techo de F1
encontrado —probando 17+ configuraciones de modelos, ingeniería de
features, resampling (incluyendo SMOTE, SMOTEENN y undersampling con test
set aislado para descartar data leakage), y evaluando 6 datasets
alternativos— está en **~44-48%**, muy por debajo del 80% exigido por el RNF-08. El cuello de
botella confirmado es el desbalance estructural de la clase minoritaria
(empresas en quiebra real son un evento raro, 3-7% en casi todos los
datasets públicos disponibles), no la cantidad de datos, columnas, ni el
algoritmo elegido. Esta evidencia respalda renegociar el umbral del RNF-08
con el docente guía, documentando el proceso como limitación conocida y
justificada en el informe final.

Adicionalmente, al integrar el modelo a la aplicación se identificó que el
dataset público usado (empresas grandes de Taiwan) no representa bien casos
extremos de insolvencia de PYME (patrimonio muy negativo), lo que puede
hacer que el semáforo de riesgo subestime casos límite reales — otra
consecuencia de depender de un dataset público sin poder validar contra
datos reales de una PYME chilena (ver restricción "Falta de Stakeholder(s)"
en el plan de proyecto, sección 4.1.5).
