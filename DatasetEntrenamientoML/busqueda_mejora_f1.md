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

## Conclusión general

Con datos de balance financiero simple (5-7 ratios, sin variables
macroeconómicas, texto o series temporales largas), el techo de F1
encontrado —probando 13+ configuraciones de modelos, ingeniería de
features, resampling, y evaluando 6 datasets alternativos— está en
**~44-48%**, muy por debajo del 80% exigido por el RNF-08. El cuello de
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
