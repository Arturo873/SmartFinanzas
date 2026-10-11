# Bitácora del modelo predictivo v8

Registro de cómo se pasó del modelo de Taiwán al modelo v8 de 8 variables, en orden. Para cada fase indica qué se hizo, qué archivos se crearon o cambiaron, las decisiones tomadas y los hallazgos.
Los detalles están en los documentos enlazados; este archivo es el índice.

**Periodo:** 5 al 11 de octubre de 2026.
**Punto de partida:** modelo Random Forest entrenado con quiebras reales de Taiwán, F1 = 46,8 % (lejos del 80 % que pedía RNF-08 v7). Ver [busqueda_mejora_f1.md](busqueda_mejora_f1.md).

## Documentos relacionados

| Documento | Contenido |
|---|---|
| [fuentes_modelo_ml.md](fuentes_modelo_ml.md) | Fuentes verificadas, umbrales por variable, regla de etiquetado y fuentes de datos |
| [requerimientos_v8_propuesta.md](requerimientos_v8_propuesta.md) | Cada requerimiento modificado: texto v7, texto v8 y fundamento |
| [Requerimientos_funcionales_y_no_funcionales_v8.xlsx](Requerimientos_funcionales_y_no_funcionales_v8.xlsx) | Documento oficial de requerimientos v8 (celdas cambiadas en verde) |
| [resultados_entrenamiento_v8.md](resultados_entrenamiento_v8.md) | Metodología del entrenamiento, resultados, limitaciones y reproducción |
| [guia_seccion_metodologia_informe.md](guia_seccion_metodologia_informe.md) | Esqueleto con el contenido de la metodología para el informe final y la defensa |
| [busqueda_mejora_f1.md](busqueda_mejora_f1.md) | Historia anterior: intentos de mejorar el modelo de Taiwán (reemplazado) |
| [correo_profesor_rnf08.md](correo_profesor_rnf08.md) | Correo al profesor sobre la meta de RNF-08 |

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
- [requerimientos_v8_propuesta.md](requerimientos_v8_propuesta.md) (creado)
- [Requerimientos_funcionales_y_no_funcionales_v8.xlsx](Requerimientos_funcionales_y_no_funcionales_v8.xlsx) (13 celdas modificadas)

**Decisiones**

| Decisión | Aprobó |
|---|---|
| **V7 normalizada:** desviación estándar del flujo neto diario / ingreso promedio diario, para comparar empresas de distinto tamaño | Usuario, 2026-10-11 |
| **Mínimo de 20 cierres de caja** para calcular V7; con menos, se usa el valor neutro | Usuario, 2026-10-11 |
| **Proporciones escritas como insolventes/solventes y sumando 100 %:** 50/50, 40/60, 30/70, 20/80 y 10/90. "80/100" del Acta se interpretó como 20/80 (conviene confirmarlo con el profesor) | Usuario, 2026-10-11 |
| Declarar en el informe que el 90-95 % se mide sobre datos sintéticos | Usuario, 2026-10-11 |
| Mantener separados el **Beta CAPM** (riesgo del sector) y el **contexto macro** (V8) | Usuario, 2026-10-11 |

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
| [resultados_entrenamiento_v8.md](resultados_entrenamiento_v8.md) | Metodología y resultados completos |

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

## Pendientes

| Pendiente | Responsable |
|---|---|
| Fase 5: sección de metodología para el informe | Equipo + Claude |
| Confirmar con el profesor que "80/100" del Acta quería decir 20/80 | Equipo |
| Implementar el módulo de caja (RF-19 a RF-22) para que V7 use datos reales | Por definir |
| Validación con datos reales de Nstock (segunda etapa, según el Acta) | Equipo |
| Quitar el resaltado verde del Excel cuando se apruebe la v8 | Equipo |
