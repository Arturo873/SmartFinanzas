# Evaluación de fuentes de datos

Proyecto SmartFinanzas, equipo Lostics. Octubre de 2026.

Este documento resume qué fuentes de datos se evaluaron para el modelo de riesgo de insolvencia, cuál se aceptó y por qué se descartaron las demás.

## Resumen

| Fuente | Qué entrega | Decisión | Uso en el proyecto |
|---|---|---|---|
| CMF, estados financieros IFRS anuales (2012-2024) | Balance y estado de resultados de 678 empresas chilenas no financieras | **Aceptada** | Entrenamiento y prueba del modelo |
| CMF, archivo de septiembre 2025 | Estados financieros de 8 empresas pequeñas y medianas por ventas | Aceptada con alcance limitado | Prueba del pipeline (carga, cálculo de variables y predicción) |
| Nstock Importaciones (empresa patrocinadora) | Datos reales de una PYME | Aceptada con alcance limitado | Prueba del sistema completo con una PYME real |
| Boletín Concursal | Empresas en procedimiento concursal (RUT, tipo de procedimiento, tribunal) | Aceptada solo para verificación | Identificar las quiebras legales entre las empresas de la CMF |
| SII, nómina de personas jurídicas | Tramos de ventas y de capital, rubro, comuna | **Descartada** | No entrega cifras contables |
| Datasets extranjeros (Taiwán, Polonia, Estados Unidos, Colombia, entre otros) | Ratios financieros y quiebras de otros países | **Descartada** | Probados antes; otro mercado y peor resultado |
| Datos sintéticos (Acta CreaEmpresas, 05-10-2026) | Empresas generadas a partir de las reales de la CMF | **Descartada como evidencia** | Solo como comparación |

Las 7 variables del modelo son: razón corriente (V1), capital de trabajo sobre activos totales (V2), leverage total (V3), ROA operacional (V4), margen operacional (V5), rotación de activos (V6) y volatilidad del flujo de caja diario (V7). V1 a V6 se calculan con el balance y el estado de resultados; V7 sale del módulo de flujo de caja de la plataforma.

---

## 1. CMF, estados financieros anuales 2012-2024 (fuente aceptada)

Fuente: https://www.cmfchile.cl/institucional/estadisticas/merc_valores/sa_eeff_ifrs/sa_eeff_ifrs_index.php?lang=es&rg_rf=RGEIN

### Qué se usó

- Estados financieros IFRS a diciembre (12 meses) que las sociedades reportan a la CMF, de 2012 a 2024.
- **678 empresas no financieras**, 5.277 empresa-año, de distintos sectores (comercio, industria, energía, inmobiliario, servicios, entre otros).
- Se dejaron fuera las empresas financieras y las que no separan su balance en corriente y no corriente, porque sin esa separación no se pueden calcular V1 y V2.

### Cómo se procesa

1. Se extraen las cuentas del balance y del estado de resultados de cada empresa y año.
2. Se calculan V1 a V6 con el mismo código que usa la plataforma (`variables_modelo.py`).
3. Cada empresa-año se etiqueta como **insolvente** si está en zona de riesgo según el Z-score de Altman para mercados emergentes (Z''EM < 1,10) o si tiene patrimonio negativo. Resultan 236 empresa-año insolventes (4,5 %).
4. Se separan las empresas en entrenamiento (542 empresas, 4.211 empresa-año) y prueba (136 empresas, 1.066 empresa-año), por empresa, para que ninguna aparezca en ambos conjuntos.

### Por qué se acepta

- Son datos reales de empresas chilenas, públicos y auditados, bajo norma IFRS.
- Traen balance y estado de resultados completos, que es lo que necesitan las variables del modelo.
- Tienen suficientes casos de insolvencia (236) para entrenar y probar el modelo.
- Resultado en la prueba con 136 empresas que el modelo nunca vio: **F1 76,8 %, Recall 74,5 %, Precisión 79,2 %, PR-AUC 85,8 %**. El accuracy es 97,8 %, pero no se usa como meta: solo el 5 % de los casos son insolventes, así que un modelo que declare solventes a todas las empresas tendría 95 % de accuracy sin detectar ninguna insolvencia.
- Cumple el objetivo específico del acta de constitución de disponer de una base de datos financieros históricos procesados y validados.

### Limitaciones

- **La etiqueta es la zona de riesgo de Altman, no la quiebra legal.** Solo 3 empresas de la CMF tienen quiebra legal en el Boletín Concursal (sección 4), demasiado pocas para entrenar.
- **Casi todas son empresas grandes.** 227 de las 678 empresas (1.180 empresa-año) son micro, pequeñas o medianas por ventas (Ley 20.416), pero incluyen holdings, inmobiliarias y empresas del Estado, no PYMEs típicas. En esas empresas de la prueba el modelo rinde mejor (F1 94,4 %, con solo 18 casos insolventes).
- **V7 no existe en la CMF**, porque no hay datos públicos de caja diaria. En el entrenamiento se simuló y en el sistema se usa un valor neutro hasta que el módulo de caja esté listo.
- **Años 2009-2011 fuera.** Usan otro formato (nombres de cuenta distintos y cuentas faltantes). Incorporarlos requiere adaptar la extracción y reentrenar, así que queda para la fase final del proyecto.

---

## 2. CMF, archivo de septiembre 2025 (prueba del pipeline)

### Qué se revisó

Estados financieros IFRS de la CMF acumulados de enero a septiembre 2025: 115 empresas y 490 columnas, con balance, estado de resultados y flujo de efectivo.

### Clasificación por tamaño (Ley 20.416, ventas anuales netas)

Micro: hasta 2.400 UF. Pequeña: más de 2.400 y hasta 25.000 UF. Mediana: más de 25.000 y hasta 100.000 UF. Grande: más de 100.000 UF.

Se toman los ingresos de actividades ordinarias, se pasan a pesos los que están en dólares, se multiplican por 12/9 para anualizar y se dividen por la UF del 30-09-2025 ($39.485,65, según el SII).

| Tamaño | Empresas |
|---|---|
| Grande | 74 |
| Mediana | 20 |
| Pequeña | 16 |
| Micro | 1 |
| Sin ingresos informados | 4 |
| Total | 115 |

De las 36 pequeñas y medianas, 28 son financieras (administradoras de fondos, leasing, hipotecarias, etc.), cuyos ingresos son comisiones o intereses y no ventas. Se marcaron por razón social y se revisaron a mano.

### Muestra resultante: 8 empresas no financieras

| Tamaño | Empresa | RUT | Ventas anuales (UF) |
|---|---|---|---|
| Mediana | Empresa Portuaria Coquimbo | 61.946.300-5 | ~94.100 |
| Mediana | Inmobiliaria Casanuestra S.A. | 76.459.878-4 | ~72.500 |
| Mediana | Servihabit S.A. (balance consolidado) | 96.783.540-4 | ~36.000 |
| Mediana | Comercializadora de Trigo S.A. | 96.511.150-6 | ~29.800 |
| Mediana | Inmobiliaria Mapsa S.A. | 96.809.690-7 | ~29.600 |
| Pequeña | EFE Arica - La Paz S.A. | 96.769.070-8 | ~17.500 |
| Pequeña | San Sebastián Inmobiliaria S.A. | 76.661.770-0 | ~8.800 |
| Pequeña | Empresa de Servicios Sanitarios Lago Peñuelas S.A. | 96.846.610-0 | ~5.200 |

Las 8 tienen balance y estado de resultados, que es lo que necesitan V1 a V6. V7 no está disponible y se usa el valor neutro.

Recomendación de uso:

- **Usar:** Mapsa, Casanuestra y Comercializadora de Trigo (datos completos). Servihabit también, porque muestra señales de debilidad (margen operacional de -19 %, liquidez corriente de 1,32) y sirve para ver cómo reacciona el modelo, aunque su balance es consolidado.
- **Marcar aparte:** Empresa Portuaria Coquimbo y EFE Arica - La Paz, que parecen de propiedad estatal (no verificado); Coquimbo muestra además un margen operacional de 183 % que hay que revisar. Lago Peñuelas es una sanitaria regulada, con ingresos más estables que una PYME comercial.

### Por qué tiene un alcance limitado

- **Sirve para probar el pipeline** con datos reales e incompletos: lectura del archivo, cálculo de las variables y salida del modelo.
- **No sirve para medir el desempeño del modelo:** ninguna de las 8 está en quiebra, así que no hay casos insolventes con los que medir F1 o Recall.
- **No son PYMEs típicas:** son sociedades anónimas que reportan a la CMF; tres son inmobiliarias, dos parecen estatales y una es una sanitaria regulada. Deben describirse como "empresas pequeñas y medianas por ventas que reportan a la CMF".
- **Son 9 meses, no 12.** El modelo se entrenó con flujos anuales, así que para la prueba los ingresos y resultados deben anualizarse o usarse el cierre de diciembre.
- **La clasificación es sensible a la anualización y a la UF:** sin anualizar resultan 18 medianas y 23 pequeñas; Coquimbo está cerca del límite con grande, y Mapsa y Trigo cerca del límite con pequeña.

---

## 3. Nstock Importaciones (prueba del sistema)

Es la empresa patrocinadora y el caso de uso real del sistema. Sus datos se usan para probar la plataforma de punta a punta con una PYME real: carga de la plantilla, validación, cálculo de las 7 variables, predicción y panel de resultados.

No se usan para entrenar ni para medir la precisión del modelo: es una sola empresa y no está en quiebra, así que no permite calcular F1 o Recall. La adopción del ERP Facto por parte de Nstock solo cambia de dónde salen sus datos (la plantilla acepta lo que exporta el ERP), no lo que se le pide al modelo.

---

## 4. Boletín Concursal (verificación de quiebras legales)

Fuente: https://www.boletinconcursal.cl/boletin/procedimientos

### Qué contiene

Registro de publicaciones de procedimientos concursales: rol de la causa, tipo de procedimiento (liquidación forzosa, voluntaria, simplificada, renegociación), deudor y RUT, liquidador, nombre de la publicación, tribunal y fecha de publicación. El registro completo trae unas 3.149 empresas en liquidación desde 2014.

### Qué no contiene

- Ninguna cifra contable (balance ni estado de resultados).
- La fecha de la quiebra: la fecha que trae es la de cada publicación.

### Cómo se usa

Se cruzó por RUT con todas las empresas de la CMF (2009-2024). **Solo 3 coinciden:** Sartor Administradora General de Fondos, Telecomunicaciones Internacionales y Claro, Vicuña, Valenzuela. Son muy pocas para entrenar, así que se usan como chequeo cualitativo: el modelo detecta en riesgo a 2 de las 3 (la tercera solo tiene datos hasta 2014, varios años antes de su quiebra).

El cruce con el archivo de septiembre 2025 da 0 coincidencias. Las empresas que quiebran son en su mayoría PYMEs que no reportan a la CMF, y no existe una fuente pública con sus balances.

### Limitaciones de la revisión

La muestra revisada a mano era de un solo día (119 filas, 16 empresas en liquidación), así que no permite contar quiebras por año. El archivo completo puede superar el límite de filas de Excel y conviene trabajarlo en CSV.

---

## 5. SII, nómina de personas jurídicas (descartada)

Fuente: https://www.sii.cl/sobre_el_sii/nominapersonasjuridicas.html

### Qué contiene

RUT, razón social, tramo de ventas (código numérico; requiere la tabla de equivalencias del SII para pasarlo a UF), número de trabajadores, fechas de inicio y término de giro, tipo de contribuyente, tramo de capital propio, rubro y actividad, región y comuna, y régimen tributario.

### Por qué se descarta

- **No trae cifras contables:** solo rangos de ventas y de capital propio, sin balance ni estado de resultados. No permite calcular ninguna de las 7 variables.
- El tramo de ventas sale de formularios tributarios y puede no reflejar el valor económico real.
- Aunque el Boletín Concursal identifica qué PYMEs quebraron, ni el SII ni otra fuente pública entrega sus balances.

### Limitaciones de la revisión

Se revisó una muestra de 125 filas del año comercial 2020, ordenadas por RUT, en su mayoría sociedades de hecho. No se pudo verificar la cobertura del archivo completo.

---

## 6. Datasets extranjeros (descartados)

Antes de usar la CMF, el modelo se entrenó con datasets públicos de otros países. Se probaron más de 17 configuraciones (algoritmos, balanceo de clases y nuevas variables):

| Dataset | F1 con la proporción real de quiebras |
|---|---|
| Taiwán (modelo anterior) | 46,8 % |
| Colombia (Superintendencia de Sociedades, 9.439 empresas) | 29,4 % |
| Polonia, Estados Unidos, Rusia, China, Eslovaquia | Techo de 44-49 % en conjunto |

Se descartan porque representan otros mercados y otras normas contables, y porque su resultado es peor que el de la CMF. Las cifras no son directamente comparables con el 76,8 % de la CMF, porque esos datasets miden quiebras legales y la CMF mide zona de riesgo de Altman.

---

## 7. Datos sintéticos (descartados como evidencia)

Por recomendación de CreaEmpresas (acta del 05-10-2026) se generaron 5 datasets sintéticos a partir de las empresas reales de la CMF, con distintas proporciones de insolventes (50/50 a 10/90), usando Borderline-SMOTE y reglas de consistencia contable.

Entrenado con ellos, el modelo obtiene en la misma prueba con empresas reales un F1 entre 71 % y 76 % y un PR-AUC de 80-82 %, contra 85,8 % del modelo entrenado solo con datos reales. Es decir, no mejoran el resultado. Su propia prueba sintética da cifras optimistas (92-99 %), porque se genera desde las mismas empresas que el entrenamiento.

El acta de constitución permitía validar el modelo con escenarios simulados. Siguiendo la indicación del profesor del curso, eso se cambia: **los datos sintéticos no se usan como evidencia de precisión** y quedan solo como comparación.
