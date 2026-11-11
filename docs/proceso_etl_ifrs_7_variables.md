# Del Archivo IFRS a las 7 Variables del Modelo: Explicación del Proceso ETL

Este documento explica, en lenguaje simple y sin tecnicismos de programación, **cómo** la plataforma transforma un balance IFRS extenso (como la plantilla oficial CMF de cientos de columnas) en **7 indicadores financieros comparables**, y **por qué** se tomaron las decisiones clave del proceso.

---

## 1. Visión General: ¿Qué problema resuelve el ETL?

Un estado financiero bajo norma **IFRS / CMF** trae cientos de columnas (alrededor de 490 en la plantilla oficial), con nombres largos, columnas repetidas o equivalentes, monedas y formatos numéricos distintos. Sin embargo, para evaluar salud financiera y riesgo de insolvencia de forma confiable entre empresas de distinto tamaño, el modelo no necesita cientos de montos brutos: necesita **7 razones financieras estandarizadas**.

El proceso sigue cuatro pasos simples:

1. **Extracción e identificación:** Ubica las 10 cuentas contables útiles (más fecha y moneda) dentro del archivo horizontal (filas = períodos, columnas = cuentas).
2. **Limpieza y validación contable:** Convierte montos a números limpios y verifica que el balance tenga sentido lógico antes de calcular nada.
3. **Reconstrucción de cuentas faltantes:** Si una cuenta clave viene vacía (como el resultado operacional), la reconstruye usando cuentas auxiliares del mismo estado financiero.
4. **Transformación a 7 variables:** Convierte los montos en pesos a **ratios adimensionales** (veces o porcentajes) protegidos contra divisiones por cero y valores extremos.

---

## 2. Decisiones de Diseño y su Porqué

| Decisión | ¿Qué se hace? | ¿Por qué se decidió así? |
| :--- | :--- | :--- |
| **Formato horizontal obligatorio** | Cada fila debe ser un período (ej. `03 / 2026`) y cada columna una cuenta contable. Si viene vertical, se rechaza con aviso claro. | Permite procesar series históricas de varios trimestres en una sola carga y coincide con el estándar de exportación de la CMF. |
| **Reducir ~490 columnas a 7 ratios** | En lugar de usar montos absolutos en pesos, se calculan 7 proporciones (`V1` a `V7`). | Un millón de pesos significa algo muy distinto en una pyme que en una gran empresa. Los ratios permiten comparar empresas de cualquier tamaño sin sesgo de escala. |
| **Prioridad de primera columna encontrada** | Cuando la taxonomía IFRS repite conceptos parecidos (ej. dos formas de llamar al *Activo Corriente*), se toma la columna principal y se ignoran las duplicadas. | Evita ambigüedades, sobreescrituras accidentales o mezclar subtotales distintos dentro de un mismo período. |
| **Respaldo automático del EBIT** | Si el *Resultado Operacional (EBIT)* viene vacío o en cero, se estima sumando `Ganancia antes de impuestos + Gastos financieros`. | Muchas empresas no informan explícitamente la línea de EBIT; reconstruirla evita perder las variables de rentabilidad (`V4` y `V5`). |
| **Bloqueo ante Activo Total <= 0** | Si el Activo Total es cero o negativo, el sistema detiene la carga del período y pide corrección. | El Activo Total es el denominador base de la escala de la empresa (`V2`, `V4`, `V6` y `V7` individual); sin él los cálculos carecen de sentido financiero. |
| **Control de ecuación patrimonial (<= 5%)** | Se revisa que `Activo Total` cuadre con `Pasivo Total + Patrimonio` (tolerancia hasta 5% por redondeos). | Garantiza calidad de datos desde el origen contable antes de alimentar el modelo predictivo. |
| **Topes en divisiones críticas y patrimonio <= 0** | Si el Pasivo Circulante o el Patrimonio son <= 0, se fija un tope (`10.0`) y se genera alerta de insolvencia técnica; además los ratios se acotan a rangos razonables. | En matemáticas, dividir por cero rompe el cálculo y un patrimonio negativo invierte el signo del endeudamiento (haría parecer "menos endeudada" a una empresa quebrada). El tope preserva el significado real de riesgo. |
| **Cálculo adaptativo de volatilidad (`V7`)** | Con **2 o más períodos**, mide qué tanto varía el flujo operacional frente al promedio de ingresos. Con **1 solo período**, mide el peso del flujo operacional sobre los activos. | No es posible calcular una desviación estándar con un solo dato; esta regla permite evaluar tanto archivos multi-período como cargas puntuales sin dejar el modelo ciego. |
| **Trazabilidad sin ruido en el modelo** | La *Moneda* (`C`) y las *Utilidades Retenidas* (`EK`) se extraen para auditoría/referencia clásica, pero no entran en `V1..V7`. | Mantiene el vector de entrada exactamente alineado con las 7 variables con las que fue entrenado el modelo predictivo. |

---

## 3. Qué Toma del Archivo IFRS (y Qué Descarta)

De toda la planilla `PlantillaIFRS.xlsx`, el ETL busca por nombre estandarizado las columnas principales e ignora automáticamente las columnas equivalentes secundarias una vez encontrada la principal:

| Columna Excel | Cuenta en el archivo IFRS | Rol en el proceso | Columnas secundarias ignoradas (si ya existe la principal) | Para qué se usa |
| :---: | :--- | :--- | :--- | :--- |
| **B** | Fecha | Metadato obligatorio | **F** (*Fecha Cierre*) | Identifica el período de cada fila (ej. `03 / 2026`). |
| **C** | Moneda | Metadato auditoría | — | Registra la moneda declarada (ej. `PESOS`). |
| **T** | Total de activos corrientes distintos de los mantenidos para la venta... | Obligatoria | **V** (*Activos corrientes totales*) | Liquidez de corto plazo (`V1`, `V2`). |
| **CC** | Total de activos | Obligatoria | — | Escala total de la empresa (`V2`, `V4`, `V6`, `V7` de 1 período) y cuadratura contable. |
| **CL** | Total de pasivos corrientes distintos de los mantenidos para la venta... | Obligatoria | **CN** (*Pasivos corrientes totales*) | Deudas de corto plazo (`V1`, `V2`). |
| **EH** | Total de pasivos | Obligatoria | — | Endeudamiento total (`V3`) y cuadratura contable. |
| **EP** | Patrimonio atribuible a los propietarios de la controladora | Obligatoria | **ER** (*Patrimonio total*) | Base patrimonial (`V3`) y detección de insolvencia técnica. |
| **EZ** | Ingresos de actividades ordinarias | Obligatoria | — | Ventas del período (`V5`, `V6` y denominador de `V7` multi-período). |
| **FR** | Ganancias (pérdidas) de actividades operacionales | Principal (con respaldo) | **GY**, **HZ** (*Resultado operacional*) | EBIT operacional (`V4`, `V5`). |
| **GC** | Ganancia (pérdida), antes de impuestos | Auxiliar de respaldo | **HC**, **IC** (*Resultado antes de impuesto*) | Solo se usa para reconstruir EBIT si **FR** falta o es `0`. |
| **FC** | Gastos por intereses y reajustes | Auxiliar de respaldo | **FU** (*Costos financieros*), **GI**, **HJ** | Solo se suma a **GC** para reconstruir EBIT si **FR** falta o es `0`. |
| **OC** | Flujos de efectivo netos procedentes de actividades de operación | Opcional (asume `0` si falta) | — | Mide estabilidad de generación de caja (`V7`). |
| **EK** | Ganancias (pérdidas) acumuladas | Opcional auditoría | — | Respaldo informativo/auditoría (no entra en `V1..V7`). |

---

## 4. Cómo se Transforman las Cuentas en las 7 Variables (`V1` a `V7`)

Cada fila del balance limpio da origen a un vector de 7 variables financieras (`V1..V7`, denominadas `X1..X7` dentro del modelo predictivo):

| Variable | Nombre | Qué mide en palabras simples | Cómo se calcula | Reglas de protección y rango normal (RF-10) |
| :---: | :--- | :--- | :--- | :--- |
| **V1** (`X1`) | **Razón Corriente** | Cuántas veces alcanza el activo de corto plazo para cubrir las deudas de corto plazo. | `Activo Circulante / Pasivo Circulante` | Si Pasivo Circulante <= 0, se fija en `10.0`. Acotada entre `0.0` y `10.0`. Rango normal: `0.20x` a `8.00x`. |
| **V2** (`X2`) | **Capital de Trabajo sobre Activos** | Qué porcentaje de los activos totales queda libre para operar después de pagar deudas inmediatas. | `(Activo Circulante - Pasivo Circulante) / Activo Total` | Requiere Activo Total > 0 (si no, error bloqueante). Se expresa como proporción / `%`. |
| **V3** (`X3`) | **Leverage Total (Endeudamiento)** | Cuántos pesos de deuda total tiene la empresa por cada peso de patrimonio propio. | `Pasivo Total / Patrimonio Neto` | Si Patrimonio <= 0, activa alerta de **Insolvencia Técnica** y fija `10.0`. Acotada entre `0.0` y `10.0`. Rango normal: `0.00x` a `7.00x`. |
| **V4** (`X4`) | **ROA Operacional** | Qué tan rentables son los activos gracias a la operación propia del negocio. | `EBIT / Activo Total` | Si falta EBIT (`FR`), usa respaldo `GC + FC`. Rango normal: `-50%` a `50%` (alerta si supera ±60%). |
| **V5** (`X5`) | **Margen Operacional** | Qué porcentaje de las ventas queda como ganancia operativa antes de intereses e impuestos. | `EBIT / Ingresos Netos` | Acotada entre `-1.0` (`-100%`) y `1.0` (`100%`). Si Ingresos <= 0: `-1.0` si EBIT < 0, o `0.0`. |
| **V6** (`X6`) | **Rotación de Activos** | Cuántas veces logra vender la empresa el equivalente a sus activos totales en el período. | `Ingresos Netos / Activo Total` | Acotada entre `0.0` y `10.0`. Rango normal: `0.05x` a `6.00x`. |
| **V7** (`X7`) | **Volatilidad del Flujo de Caja** | Qué tan inestable o riesgosa es la entrada de efectivo operacional frente al nivel de ventas. | **>= 2 períodos:** `Desv. Estándar(Flujo Op.) / Promedio(Ingresos)` <br> **1 período:** `Valor absoluto(Flujo Op. / Activo Total)` | Si el promedio de ingresos (o Activo Total en 1 período) es <= 0, toma valor neutro `0.0`. |

---

## 5. Ejemplo Real Trazado (Caso CMF `03 / 2026` y `06 / 2026`)

Para ilustrar cómo entran los datos crudos y salen las 7 variables en un período real (`03 / 2026`, usando además `06 / 2026` únicamente para la variabilidad de `V7`):

**Datos extraídos del archivo IFRS (`03 / 2026`):**
- Activo Circulante (`T`): `2.604.212.000`
- Pasivo Circulante (`CL`): `530.733.000`
- Activo Total (`CC`): `15.149.324.000`
- Pasivo Total (`EH`): `530.733.000`
- Patrimonio Neto (`EP`): `14.618.591.000`
- Ingresos Netos (`EZ`): `234.554.000` *(y `576.145.000` en `06 / 2026`)*
- EBIT (`FR`): `-80.237.000` *(como es distinto de `0`, **no** se activa el respaldo `GC = 115.780.000` + `FC = 0`)*
- Flujo Operacional (`OC`): `303.926.000` *(y `286.563.000` en `06 / 2026`)*

**Transformación resultante:**

| Variable | Operación aplicada | Valor final | Lectura financiera |
| :---: | :--- | :---: | :--- |
| **V1** | `2.604.212.000 / 530.733.000` | **`4,9068`** (`4,91x`) | Liquidez holgada: cubre casi 5 veces sus deudas de corto plazo. |
| **V2** | `(2.604.212.000 - 530.733.000) / 15.149.324.000` | **`0,1369`** (`13,69%`) | El 13,69% del activo total corresponde a capital de trabajo neto. |
| **V3** | `530.733.000 / 14.618.591.000` | **`0,0363`** (`0,04x`) | Endeudamiento muy bajo respecto a su patrimonio. |
| **V4** | `-80.237.000 / 15.149.324.000` | **`-0,0053`** (`-0,53%`) | Leve pérdida operativa respecto al tamaño total de sus activos. |
| **V5** | `-80.237.000 / 234.554.000` | **`-0,3421`** (`-34,21%`) | El resultado operacional del trimestre fue negativo frente a sus ventas. |
| **V6** | `234.554.000 / 15.149.324.000` | **`0,0155`** (`0,02x`) | Baja rotación trimestral de ventas sobre la base total de activos. |
| **V7** | `std(303.926.000, 286.563.000) / mean(234.554.000, 576.145.000)` = `12.277.495 / 405.349.500` | **`0,0303`** | Volatilidad de caja baja y estable entre ambos trimestres. |
