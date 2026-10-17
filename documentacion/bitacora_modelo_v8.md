# Bitácora del modelo predictivo v8

Registro de cómo se pasó del modelo de Taiwán al modelo v8 de 8 variables, en orden. Para cada fase indica qué se hizo, qué archivos se crearon o cambiaron, las decisiones tomadas y los hallazgos.
Los detalles están en los documentos enlazados; este archivo es el índice.

**Periodo:** 5 al 16 de octubre de 2026 (al final se agregan los modelos v10 y v11 y la propuesta formal al profesor; el v11, vigente, se entrena solo con datos reales).
**Punto de partida:** modelo Random Forest entrenado con quiebras reales de Taiwán, F1 = 46,8 % (lejos del 80 % que pedía RNF-08 v7). Ver [busqueda_mejora_f1.md](busqueda_mejora_f1.md).

## Documentos relacionados

| Documento | Contenido |
|---|---|
| [fuentes_modelo_ml.md](fuentes_modelo_ml.md) | Fuentes verificadas, umbrales por variable, regla de etiquetado y fuentes de datos |
| [Requerimientos_funcionales_y_no_funcionales_v11.xlsx](Requerimientos_funcionales_y_no_funcionales_v11.xlsx) | Documento oficial de requerimientos vigente (v11: RNF-08 con datos reales, PR-AUC ≥ 80 % y Recall y F1 ≥ 70 %) |
| [Requerimientos_funcionales_y_no_funcionales_v10.xlsx](Requerimientos_funcionales_y_no_funcionales_v10.xlsx) | Requerimientos v10 (7 variables, sin RF-01, RNF-08 sintético); reemplazado por la v11 |
| [Requerimientos_funcionales_y_no_funcionales_v9.xlsx](Requerimientos_funcionales_y_no_funcionales_v9.xlsx) | Requerimientos v9 (sin CAPM, 8 variables); reemplazado por la v10 |
| [Requerimientos_funcionales_y_no_funcionales_v8.xlsx](Requerimientos_funcionales_y_no_funcionales_v8.xlsx) | Requerimientos v8 (celdas cambiadas en verde); reemplazado por la v9 |
| [resultados_entrenamiento_v11.md](resultados_entrenamiento_v11.md) | Metodología del entrenamiento, resultados, limitaciones y reproducción |
| [guia_seccion_metodologia_informe.md](guia_seccion_metodologia_informe.md) | Esqueleto con el contenido de la metodología para el informe final y la defensa |
| [busqueda_mejora_f1.md](busqueda_mejora_f1.md) | Historia anterior: intentos de mejorar el modelo de Taiwán (reemplazado) |
| [correo_profesor_rnf08.md](correo_profesor_rnf08.md) | Correo al profesor sobre la meta de RNF-08 (anterior, modelo de Taiwán) |
| [Correo (lo que dijo el profe)](<Correo (lo que dijo el profe)>) | Solicitud del profesor Covarrubias: propuesta formal antes del 19-10-2026 |
| [CorreoAlprofe_v2.docx](CorreoAlprofe_v2.docx) / [.md](CorreoAlprofe_v2.md) | Respuesta al profesor: alcance, ML, datos reales, validación y cambios respecto del acta |
| [EvaluacionFuentesDatos.docx](EvaluacionFuentesDatos.docx) / [.md](EvaluacionFuentesDatos.md) | Anexo del correo: fuentes aceptadas y descartadas (reemplaza a DatosDescartados.docx) |
| [Informe_SmartFinanzas_v14.docx](Informe_SmartFinanzas_v14.docx) | Informe con la primera parte alineada al modelo v11, en control de cambios |
| [Lostics_Acta-de-Constitucion_FINAL.docx](Lostics_Acta-de-Constitucion_FINAL.docx) | Proyecto originalmente aprobado (objetivos, alcance y meta de 80 %) |

## Origen del cambio

| Fecha | Hecho | Fuente |
|---|---|---|
| 2026-10-05 | Reunión con CreaEmpresas Inacap (profesor Juan Pablo Yáñez): entrenar con **datos sintéticos en múltiples proporciones**, meta de **90 % mínimo y 95 % ideal**, mantener Machine Learning (redes neuronales como trabajo futuro) y reservar los datos de Nstock para una validación posterior | Acta de reunión 05-10-2026 |
| 2026-10-10 | Lectura del tablero Miro "SmartFinanzas": **8 variables**, entrenar desde cero, Borderline-SMOTE y reglas axiomáticas | Tablero Miro `uXjVEdfTbh4=` |
| 2026-10-11 | El equipo elige el **camino 3 (completo)**: adoptar las 8 variables del Miro en el código, los requerimientos y el informe | Decisión del equipo |

Los tres caminos evaluados fueron: (1) mantener los 7 ratios y cambiar solo el entrenamiento; (2) adoptar V1 a V6; (3) adoptar las 8 variables.

## Fase 1: Fuentes (2026-10-11)

**Qué se hizo**
- Se verificaron 10 referencias con DOI o enlace.
- Se leyeron completos Riquelme (2018), Ríos et al. (2018), Zurita (2008) y Ringeling (2004). La tesis de Ringeling la descargó a mano el equipo, porque el repositorio de la U. de Chile bloquea descargas automáticas.
- Se extrajeron los umbrales de riesgo de cada variable, con página exacta.

**Archivos**
- [fuentes_modelo_ml.md](fuentes_modelo_ml.md) (creado)
- `DatasetSinteticoEntrenamientoML/ringeling_e.pdf` (agregado por el equipo)

**Hallazgos**
- **Ríos et al.** es de 2018, no de 2017 como decía el Miro.
- **Ringeling (2004)** no es una tesis sino un *seminario de título*; por eso el repositorio lo lista con el nombre del profesor guía (Rafael Romero).
- **Zurita (2008)** usa tres variables macro: PIB, tasa de interés y **tipo de cambio real**. El Miro solo nombraba las dos primeras.
- **Zurita (2008, p. 29):** el efecto macro sobre una empresa individual es pequeño (+0,33 % ante un deterioro de una desviación estándar).
- **Ringeling (2004, p. 75):** respalda V7 (más volatilidad, más probabilidad de quiebra).
- **Ninguna fuente da umbrales para V6 ni V7.**

**Decisiones**

| Decisión | Aprobó |
|---|---|
| Agregar el **tipo de cambio real** a V8, para ser fiel a Zurita | Usuario, 2026-10-11 |
| Agregar la columna **Utilidades_Retenidas** a la plantilla, para usar el Z-score de Altman completo | Usuario, 2026-10-11 |
| Etiquetar la clase insolvente con reglas de la literatura y usar SMOTE solo para densificar | Usuario, 2026-10-11 |
| Simular V7 en el entrenamiento y, en el sistema, usar los datos de caja reales o un valor neutro | Usuario, 2026-10-11 |
| Patrimonio negativo = Leverage en su valor de riesgo máximo | Usuario, 2026-10-11 |

## Fase 2: Requerimientos (2026-10-11)

**Qué se hizo**
- Se redactaron las versiones v8 de los requerimientos afectados por las 8 variables.
- Se aplicaron al Excel oficial, resaltadas en verde.

**Requerimientos cambiados:** RF-01, RF-03, RF-05, RF-08, RF-09, RF-10, RNF-05, RNF-08, RNF-09 y RNF-10. El resto no cambia.

**Archivos**
- `requerimientos_v8_propuesta.md` (creado; eliminado el 2026-10-15, ver [Exclusión del CAPM](#exclusión-del-capm-2026-10-15))
- [Requerimientos_funcionales_y_no_funcionales_v8.xlsx](Requerimientos_funcionales_y_no_funcionales_v8.xlsx) (13 celdas modificadas)

**Decisiones**

| Decisión | Aprobó |
|---|---|
| **V7 normalizada:** desviación estándar del flujo neto diario / ingreso promedio diario, para comparar empresas de distinto tamaño | Usuario, 2026-10-11 |
| **Mínimo de 20 cierres de caja** para calcular V7; con menos, se usa el valor neutro | Usuario, 2026-10-11 |
| **Proporciones escritas como insolventes/solventes y sumando 100 %:** 50/50, 40/60, 30/70, 20/80 y 10/90. "80/100" del Acta se interpretó como 20/80 (conviene confirmarlo con el profesor) | Usuario, 2026-10-11 |
| Declarar en el informe que el 90-95 % se mide sobre datos sintéticos | Usuario, 2026-10-11 |
| Mantener separados el **Beta CAPM** (riesgo del sector) y el **contexto macro** (V8). *Revertida el 2026-10-15: el CAPM se eliminó (ver [Exclusión del CAPM](#exclusión-del-capm-2026-10-15)).* | Usuario, 2026-10-11 |

## Fase 3: Código del sistema (2026-10-11)

**Qué se hizo**

| Cambio | Requerimiento | Archivo |
|---|---|---|
| Fórmulas de las 8 variables, sus topes y el Z-score de Altman, en un solo módulo que también usa el entrenamiento | RF-10, RNF-09 | `AppWeb/variables_modelo.py` (nuevo) |
| Descarga de PIB, tasa UF y tipo de cambio real desde las tablas públicas del Banco Central (sin registro), guardadas en un CSV | RF-01, RNF-09 | `AppWeb/datos_macro.py` (nuevo), `AppWeb/datos_macro/indicadores_macro.csv` (nuevo, 2009-Q1 a 2026-Q3) |
| Comando para actualizar los datos macro: `python manage.py actualizar_datos_macro` | RF-01 | `AppWeb/management/commands/actualizar_datos_macro.py` (nuevo) |
| La plantilla exige **Ingresos_Netos, EBIT y Utilidades_Retenidas** (Patrimonio_Neto ya existía) | RF-08 | `AppWeb/views.py` |
| Rechaza archivos con activo corriente mayor que el activo total, o pasivo corriente mayor que el pasivo total | RF-09 | `AppWeb/views.py` |
| La pantalla de carga muestra las columnas requeridas | RF-08 | `AppWeb/templates/AppWeb/cargaDatos.html` |
| La pantalla de resultados muestra la tabla de las 8 variables y el trimestre del dato macro usado | RF-01, RF-10 | `AppWeb/templates/AppWeb/resultado_prediccion.html` |
| Pruebas automáticas de fórmulas, datos macro y flujo de carga y predicción | — | `AppWeb/tests.py` |
| Archivo de prueba de 5.000 filas con las columnas nuevas (datos inventados) | RNF-04 | `PlantillasPrueba/generar_prueba_v8.py`, `PlantillasPrueba/carga_masiva_sintetica_5k_v8.csv` |

**Hallazgos**
- **El módulo de caja (RF-19 a RF-22) no existe en el código:** no hay ventas, retiros ni cierres diarios. Por eso V7 siempre toma el valor neutro. La fórmula está lista y probada para cuando exista ese módulo.
- **El Banco Central no publica el tramo de 30-89 días en UF.** Zurita usa captación UF de 30 a 365 días; se usa la de **90 días a 1 año**.
- **El Excel público de PIB del Banco Central llega solo a 2020,** pero las tablas de la Base de Datos Estadísticos (BDE) tienen datos hasta 2026 y no exigen registro.
- Los archivos de prueba antiguos ya no se pueden cargar, porque no tienen las columnas nuevas.
- **Rendimiento:** la carga de 5.000 filas tarda 0,33 s (RNF-04 exige menos de 3 s).

**Incidente al subir a GitHub**

El commit de esta fase incluía ~1,8 GB de datos crudos de búsquedas anteriores, con archivos de hasta 666 MB. GitHub cortó la subida (error 408) y además rechaza archivos de más de 100 MB.

Se rehízo el commit sin esos datos y se agregaron al `.gitignore`:
- `colombia_supersociedades/financieros_raw/`
- `chile_cmf_boletin/cmf_raw/`
- `chile_cmf_boletin/boletin_concursal_raw.csv`

Los archivos siguen en el computador local y se pueden regenerar con los scripts de sus carpetas.

**Commit:** `b250245`

## Fase 4: Datos sintéticos y entrenamiento (2026-10-11)

**Qué se hizo**
1. **Paso 1:** se extrajeron **5.277 empresa-año de 678 empresas** chilenas reales de la CMF (balances a diciembre, 2012-2024), con las 8 variables calculadas por el mismo código del sistema.
2. **Etiquetado** con la regla de Altman (ver decisión).
3. **Paso 2:** se separó el 20 % de las empresas para una prueba real nunca vista. Luego se generaron 5 datasets sintéticos de 10.000 filas con Borderline-SMOTE, identidad DuPont y reglas axiomáticas.
4. **Paso 3:** se entrenó un Random Forest por proporción y se evaluó en la prueba sintética y en la prueba real.
5. **Modelo elegido: 50/50.** Se conectó al sistema y reemplazó al de Taiwán.

**Archivos**

| Archivo | Descripción |
|---|---|
| `DatasetSinteticoEntrenamientoML/paso1_extraer_cmf.py` | Extrae las empresas reales de la CMF → `cmf_empresas_reales.csv` |
| `DatasetSinteticoEntrenamientoML/paso2_generar_sinteticos.py` | Separa la prueba real y genera los datasets → `real_entrenamiento.csv`, `real_prueba.csv`, `sintetico_XX_YY.csv` (5 archivos) |
| `DatasetSinteticoEntrenamientoML/paso3_entrenar_evaluar.py` | Entrena y evalúa → `resultados_entrenamiento.csv` y el modelo |
| `AppWeb/modelo_oficial/modelo_riesgo_v8.joblib`, `metricas_v8.joblib` | Modelo en uso y sus métricas (reemplazan a los 3 archivos del modelo de Taiwán, eliminados) |
| `AppWeb/viewsML.py` | Reescrito: predicción con el modelo v8, explicabilidad por variable (RF-03) y recomendaciones por grupo (RF-05) |
| `AppWeb/views.py` | La predicción y la tendencia por período usan el modelo v8 |
| `AppWeb/templates/AppWeb/resultado_prediccion.html`, `resultado_prediccion_pdf.html` | Panel de explicabilidad en "puntos de riesgo" y F1 con empresas reales |
| `requirements.txt` | Se agrega `imbalanced-learn` (lo usan los scripts de entrenamiento) |
| [resultados_entrenamiento_v11.md](resultados_entrenamiento_v11.md) | Metodología y resultados completos |

**Decisiones**

| Decisión | Motivo | Aprobó |
|---|---|---|
| **Etiqueta = Z''EM < 1,10 o patrimonio ≤ 0**, en vez de Z1 < 1,23 | Z1 marcaba al 40 % de las empresas de la CMF como insolventes, porque castiga la baja rotación de activos; Z''EM (Altman para mercados emergentes, citado en Riquelme, 2018) marca al 4,5 % | Usuario, 2026-10-11 |
| Las 3 quiebras legales reales se usan **solo como chequeo ilustrativo**, no para entrenar | Con 3 casos no se puede entrenar ni calcular métricas | Usuario, 2026-10-11 |
| Elegir el mejor F1 en empresas reales **entre los modelos que cumplen el 90 %** en la prueba sintética | El 10/90 tenía mejor F1 real, pero no cumplía la meta de RNF-08 | Criterio de RNF-08 |
| Los montos de resultado de la plantilla deben ser de los **últimos 12 meses** | El modelo se entrenó con estados anuales; con un solo trimestre, el ROA y la rotación saldrían 4 veces más bajos | Agregado a RF-08 (Excel C18) |
| V7 simulada con `log(V7) = log(0,30) + 0,10 · leverage + ruido` | No hay datos públicos de caja diaria; la dirección sigue a Ringeling (2004, p. 87) | Supuesto de diseño, declarado como limitación |

**Resultados principales**

| Medición | Accuracy | F1 | Recall |
|---|---|---|---|
| Prueba sintética, modelo 50/50 (RNF-08) | 98,7 % | 98,7 % | 99,1 % |
| Empresas reales nunca vistas, sin datos de caja (situación actual) | 96,9 % | 69,7 % | 74,5 % |

- Cumplen la meta mínima de 90 %: 4 de 5 proporciones (la 10/90 queda en F1 = 89,9 %).
- Quiebras reales detectadas: 2 de 3.

**Otros cambios**
- Se corrigió un error que ya existía: las barras del panel de explicabilidad se veían vacías, porque su ancho nunca se aplicaba.
- Rendimiento: una predicción completa con 5.000 filas tarda 0,61 s (RNF-05 exige menos de 3 s).
- Pruebas automáticas: 15, todas pasan.

**Commit:** `e12d983`

## Exclusión del CAPM (2026-10-15)

**Origen:** reunión con la profesora asesora Carolina San Martín (Área de Administración y Negocios). Se acordó quitar el CAPM del núcleo del modelo predictivo de insolvencia, porque el CAPM corresponde a la **tasa exigida por un inversionista** y no es un ratio de solvencia.

**Qué se hizo**

| Cambio | Archivo |
|---|---|
| Se quitó la selección de sector y el ajuste por Beta después del modelo. El flujo queda en 2 pasos: el Contador carga el archivo y el Dueño ejecuta la predicción | `AppWeb/views.py`, plantillas, migración `0003_quitar_capm` (commit `f30230b`) |
| RF-01 se reescribió: solo pide el contexto macroeconómico (PIB, tasa de captación UF y tipo de cambio real). RNF-09 ya no menciona el CAPM | [Requerimientos_funcionales_y_no_funcionales_v9.xlsx](Requerimientos_funcionales_y_no_funcionales_v9.xlsx) |
| En las dos tablas del Miro, V8 pasó de "Riesgo Sistémico (CAPM)" a **"Contexto Macroeconómico"**, con los 3 indicadores de Zurita | Tablero Miro `uXjVEdfTbh4=` |
| Se quitó la mención del Beta CAPM de la metodología y de las limitaciones | [guia_seccion_metodologia_informe.md](guia_seccion_metodologia_informe.md) |
| Se eliminó `requerimientos_v8_propuesta.md`. Era el borrador del paso de v7 a v8: su contenido ya está en el Excel oficial y su RF-01 seguía basado en el CAPM. Se puede recuperar desde git (commit `b250245`) | — |

**Decisiones**

| Decisión | Aprobó |
|---|---|
| Excluir el CAPM del modelo y de los requerimientos | Profesora Carolina San Martín y equipo, 2026-10-15 |
| V8 mantiene los **3 indicadores** de Zurita (no se reduce solo al PIB): ya están implementados y entrenados, y así se conserva el respaldo bibliográfico completo | Usuario, 2026-10-15 |

El modelo v8 no cambia: el Beta se aplicaba después de la predicción, así que no era una de sus variables.

**Revisión posterior (mismo día)**

| Hallazgo | Decisión | Archivo |
|---|---|---|
| El Random Forest recibe **10 columnas**: V8 entra como 3 indicadores separados. La tabla de RF-10 mostraba 10 filas y el top 3 de RF-03 podía listar indicadores de V8 por separado | **8 variables = 10 entradas.** Se aclara en RF-01 y RF-10, y en pantalla V8 se muestra y evalúa como una sola variable (sus 3 indicadores cambian juntos al calcular el impacto). El modelo no se reentrena | `AppWeb/variables_modelo.py`, `AppWeb/viewsML.py`, `AppWeb/views.py`, `resultado_prediccion.html`, `AppWeb/tests.py` (17 pruebas, todas pasan), Excel v9, Miro |
| RF-03 hablaba de "mayor peso estadístico" sin definirlo ni decir qué pasa con V8 | La validación describe el método real: impacto si la variable toma el valor típico de una empresa solvente; en V8 cambian sus 3 indicadores a la vez | Excel v9, [guia_seccion_metodologia_informe.md](guia_seccion_metodologia_informe.md) |
| RNF-08 no decía que el 90 % se mide sobre la prueba sintética | Se agrega "sobre esa prueba sintética" y el reporte aparte con el 20 % de empresas reales de la CMF (F1 = 69,7 %) | Excel v9 |

## Modelo v10: de 8 a 7 variables (2026-10-16)

**Origen:** el equipo decidió simplificar el modelo a 7 variables y quitar V8 (contexto macroeconómico). En el tablero Miro, V8 había sido primero el CAPM y después el contexto macro; con este cambio ya no queda una octava variable. RF-01 se retiró en los Requerimientos v10.

**Qué se hizo**

| Cambio | Archivo |
|---|---|
| El modelo usa solo V1 a V7: se quitaron los 3 indicadores macro y la agrupación de V8 | `AppWeb/variables_modelo.py`, `AppWeb/viewsML.py` |
| Se eliminó la descarga de datos del Banco Central y su comando | `AppWeb/datos_macro.py`, `AppWeb/datos_macro/`, `actualizar_datos_macro.py` (eliminados) |
| La predicción ya no busca el trimestre macro, y la pantalla de resultados ya no lo muestra | `AppWeb/views.py`, `resultado_prediccion.html` |
| El paso 1 ya no agrega datos macro; el paso 2 quita la regla axiomática "en recesión no hay rentabilidades extremas", que dependía del PIB | `paso1_extraer_cmf.py`, `paso2_generar_sinteticos.py` |
| Reentrenamiento con los mismos datos de la CMF (5.277 empresa-año) y la misma semilla | `paso3_entrenar_evaluar.py`, `AppWeb/modelo_oficial/modelo_riesgo_v10.joblib`, `metricas_v10.joblib` (reemplazan a los archivos v8) |
| Se quitan `requests`, `beautifulsoup4` y `lxml`, que solo usaban el CAPM y los datos macro | `requirements.txt` |
| Pruebas actualizadas: 13, todas pasan | `AppWeb/tests.py` |
| Resultados, guía de metodología y fuentes actualizados | [resultados_entrenamiento_v11.md](resultados_entrenamiento_v11.md), [guia_seccion_metodologia_informe.md](guia_seccion_metodologia_informe.md), [fuentes_modelo_ml.md](fuentes_modelo_ml.md) |

**Resultados (modelo elegido 50/50)**

| Medición | Modelo v8 (8 variables) | Modelo v10 (7 variables) |
|---|---|---|
| Prueba sintética: Accuracy / F1 | 98,7 % / 98,7 % | 98,4 % / 98,4 % |
| Empresas reales, con V7 simulada: F1 | 71,3 % | 76,2 % |
| Empresas reales, sin datos de caja (situación actual): F1 | 69,7 % | 73,6 % |
| Proporciones que cumplen el 90 % | 4 de 5 | 5 de 5 |

Quitar V8 no empeoró el modelo: la prueba sintética queda prácticamente igual y la prueba con empresas reales mejora. Esto coincide con Zurita (2008, p. 29), que muestra que el efecto macro sobre una empresa individual es pequeño.

## Modelo v11: entrenamiento solo con datos reales (2026-10-16)

**Origen:** el profesor del curso pidió una propuesta formal (plazo: 2026-10-19) y aclaró que los datos sintéticos **no se aceptan como evidencia** de precisión ni de generalización. Se probó entrenar el mismo Random Forest solo con las empresas reales de la CMF, y el resultado con empresas nunca vistas fue igual o mejor que con los sintéticos. El equipo decidió usar ese modelo como oficial.

**Qué se hizo**

| Cambio | Archivo |
|---|---|
| El modelo oficial se entrena con las 542 empresas reales de entrenamiento (4.211 empresa-año), sin sintéticos. Los 5 datasets sintéticos del Acta se siguen entrenando, solo como comparación | `paso3_entrenar_evaluar.py`, `resultados_entrenamiento.csv` |
| Nuevos archivos del modelo (reemplazan a los v10) | `AppWeb/modelo_oficial/modelo_riesgo_v11.joblib`, `metricas_v11.joblib` |
| La app muestra Accuracy, Recall y F1 de la prueba con empresas reales (antes, de la prueba sintética) y describe el modelo como "Empresas chilenas reales de la CMF (2012-2024)" | `AppWeb/viewsML.py`, `AppWeb/views.py`, `resultado_prediccion.html`, `resultado_prediccion_pdf.html` |
| El test de RNF-08 exige Recall y F1 ≥ 70 % en la prueba real (antes 90 % en la prueba sintética); más tarde ese día se agregó PR-AUC ≥ 80 % (ver la sección siguiente). 13 pruebas, todas pasan | `AppWeb/tests.py` |
| Análisis por tamaño de empresa (Ley 20.416) | `paso4_analisis_tamano.py` (nuevo) |
| Resultados y guía de metodología actualizados | [resultados_entrenamiento_v11.md](resultados_entrenamiento_v11.md), [guia_seccion_metodologia_informe.md](guia_seccion_metodologia_informe.md) |

**Resultados (prueba con 136 empresas reales nunca vistas, sin datos de caja)**

| Medición | Modelo v10 (sintético 50/50) | Modelo v11 (solo reales) |
|---|---|---|
| F1 | 73,6 % | 76,8 % |
| Recall | 76,5 % | 74,5 % |
| Precisión | 70,9 % | 79,2 % |
| PR-AUC | 74,3 % | 85,8 % |

**Decisiones y hallazgos**

| Tema | Decisión o hallazgo |
|---|---|
| Quiebra legal contra insolvencia | Al principio no había casos reales porque se buscaban quiebras legales (solo 3 en la CMF). Con la etiqueta de zona de riesgo de Altman hay 236 casos reales, suficientes para entrenar |
| ¿Las empresas de la CMF son PYMEs? | No son PYMEs típicas. Los sintéticos tampoco lo eran, porque se generaban desde las mismas empresas. El 22 % de las empresa-año es micro, pequeña o mediana por ventas; en ellas el modelo rinde mejor que en las grandes (F1 94,4 % contra 66,7 %, con 18 insolventes PYME) |
| ¿Entrenar solo con PYMEs? | No: un modelo entrenado solo con empresa-año PYME (57 insolventes) rinde un poco peor en todos los conjuntos. Se entrena con todas las empresas |
| V7 como coeficiente de variación | Se propuso cambiar V7 a desviación estándar / promedio del flujo neto. Se mantiene la fórmula actual (desviación estándar / ingreso promedio diario, RNF-10), que ya es adimensional y no se dispara cuando el flujo neto promedio es cercano a cero o negativo |
| Años 2009-2011 | Los archivos de la CMF los traen, pero 2010-2011 no tienen "Total de pasivos" y 2009 usa nombres de cuenta antiguos. Se mantiene 2012-2024; recuperarlos queda pendiente |

## Propuesta formal al profesor (2026-10-16)

**Origen:** el profesor Carlos Covarrubias pidió por correo una propuesta formal antes del 19-10-2026, con los cambios respecto del proyecto aprobado y su justificación. Puso como no negociables que el Machine Learning siga siendo el eje, que los datos sintéticos no son evidencia de precisión y que la compra de un ERP no justifica reducir el alcance.

**Qué se hizo**

| Cambio | Archivo |
|---|---|
| Respuesta al profesor: 5 puntos de datos, 5 del proyecto, tabla de objetivos del acta, cambios con justificación y limitaciones | [CorreoAlprofe_v2.docx](CorreoAlprofe_v2.docx) |
| `DatosDescartados.docx` convertido en evaluación de fuentes: CMF aceptada; septiembre 2025, Nstock y Boletín con alcance limitado; SII, datasets extranjeros y sintéticos descartados | [EvaluacionFuentesDatos.docx](EvaluacionFuentesDatos.docx) |
| RNF-08 v11: entrenamiento con datos reales; meta PR-AUC ≥ 80 % y Recall y F1 ≥ 70 % en la prueba real (solo cambia la celda C47) | [Requerimientos v11](Requerimientos_funcionales_y_no_funcionales_v11.xlsx) |
| Informe: 30 cambios en control de cambios, solo en la primera parte (entrenamiento con la CMF, meta, V7 citada a Ringeling, citas sin verificar quitadas, comparación propia con Regresión Logística, bibliografía) | [Informe_SmartFinanzas_v14.docx](Informe_SmartFinanzas_v14.docx) |
| Regresión Logística implementada como contraste (mismos datos reales, misma prueba) | `paso3_entrenar_evaluar.py`, `resultados_entrenamiento.csv`, [resultados_entrenamiento_v11.md](resultados_entrenamiento_v11.md) §3.2b |
| La app expone el PR-AUC y el test de RNF-08 revisa PR-AUC ≥ 80 % además de Recall y F1 ≥ 70 %. 13 pruebas, todas pasan | `AppWeb/viewsML.py`, `AppWeb/tests.py` |
| Barboza, Kimura y Altman (2017) agregada como R11 | [fuentes_modelo_ml.md](fuentes_modelo_ml.md) |

**Decisiones y hallazgos**

| Tema | Decisión o hallazgo |
|---|---|
| Meta del RNF-08 | Se evaluaron 70 % (cumple), 80 % en Recall y F1 (no cumple: 74,5 % y 76,8 %) y una meta mixta. El equipo eligió la mixta: **PR-AUC ≥ 80 % y Recall y F1 ≥ 70 %**, que conserva el 80 % del acta en una métrica robusta al desbalance (Saito y Rehmsmeier, 2015). El modelo cumple las tres (85,8 %, 74,5 % y 76,8 %) |
| Accuracy | Se informa (97,8 %) pero no es meta: con 5 % de insolventes, declarar todo solvente da 95 % de accuracy. El acta de constitución lo tenía como factor crítico (≥ 80 %), así que se explica en vez de omitirlo |
| Regresión Logística | El informe la nombraba como contraste sin estar implementada. Ahora sí: F1 69,2 %, PR-AUC 75,8 %; queda bajo el Random Forest y no cumple la meta. Reemplaza las cifras de Samara y Shinde y de Gabrielli que citaba el informe |
| Comparación con el acta de constitución | La meta original era "precisión mínima de 80 %" (accuracy en los factores críticos). El CAPM y los "indicadores económicos" estaban en los objetivos. Inventario y módulo de caja **no** estaban en el alcance: retirar RF-12 a RF-18 vuelve al alcance aprobado, y el módulo de caja se declara como agregado. El acta permitía validar con escenarios simulados; se cambia por indicación del profesor |
| Retiro de RF-12 a RF-18 | No se justifica con el ERP Facto (el profesor lo descartó como razón), sino porque esos módulos no alimentan al modelo y no estaban en el acta |
| Años 2009-2011 de la CMF | Se declaran como trabajo de la fase final, una vez terminado el sistema |
| Otras empresas | No hay ninguna comprometida; el equipo gestionará con CreaEmpresas el contacto con otra empresa |
| Acta del 14-10-2026 (Carolina San Martín) | Validó las 7 variables y el retiro del CAPM; revisará a mano los cálculos de una empresa de la CMF y de las quiebras legales. El acta escribe "Caracuña": corresponde a Claro, Vicuña, Valenzuela |
| Citas | Se quitaron del correo y del informe las no verificadas (Wang, Samara y Shinde, Gabrielli, ELE 5/INE, Kokczyński) y las metas inventadas (Recall 90 %, F1 0,88). Barboza et al. (2017) se verificó por DOI y una fuente secundaria |

## Pendientes

| Pendiente | Responsable |
|---|---|
| Revisión de Arturo del correo, la evaluación de fuentes, el informe v14 y el Excel v11 | Arturo |
| Enviar el correo y la evaluación de fuentes al profesor (plazo 19-10-2026) | Equipo |
| Corregir "Caracuña" por "Claro, Vicuña, Valenzuela" en el acta del 14-10 | Equipo |
| Aceptar el control de cambios del informe v14 cuando se apruebe | Equipo |
| Actualizar la segunda parte del informe (Desarrollo e implementación) | Equipo + Claude |
| Conseguir otra empresa que aporte datos, a través de CreaEmpresas | Equipo |
| Fase 5: sección de metodología para el informe | Equipo + Claude |
| Implementar el módulo de caja (RF-19 a RF-22) para que V7 use datos reales | Por definir |
| Validación con datos reales de Nstock (segunda etapa, según el Acta) | Equipo |
| Recuperar los años 2009-2011 de la CMF (pasivo = activo − patrimonio; nombres de cuenta de 2009); fase final | Por definir |
| Quitar el resaltado verde del Excel cuando se apruebe la v8 | Equipo |
