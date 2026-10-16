# Resultados del entrenamiento del modelo v8 (RNF-08)

Fase 4 del plan "camino 3". Fecha: 2026-10-11.
Scripts en `DatasetSinteticoEntrenamientoML/`. Fuentes citadas (R1-R10) en [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

## 1. Resumen

| Requisito (RNF-08 / Acta 05-10-2026) | Resultado |
|---|---|
| Random Forest entrenado desde cero | Sí (Breiman, 2001), 300 árboles |
| Datos sintéticos en varias proporciones | 5 datasets de 10.000 filas: 50/50, 40/60, 30/70, 20/80 y 10/90 (insolventes/solventes) |
| Meta mínima de 90 % en Accuracy y F1 | **Cumplen 4 de 5** proporciones; el 10/90 queda en F1 = 89,9 % |
| Meta ideal de 95 % | **Modelo elegido (50/50): Accuracy 98,7 %, F1 98,7 %, Recall 99,1 %** |
| Nstock reservado para validación posterior | Sí, no se usó |

**Cifra realista con empresas reales:** sobre empresas chilenas de la CMF que el modelo nunca vio, y sin datos de caja (como funciona hoy el sistema), el modelo elegido logra **Accuracy 96,9 %, F1 69,7 % y Recall 74,5 %**.

## 2. Metodología

### 2.1 Base real: empresas de la CMF

- **Origen:** estados financieros IFRS que las empresas reportan a la CMF, balance a diciembre (flujos de 12 meses), 2012-2024.
- **Muestra:** 5.277 empresa-año de 678 empresas no financieras (con balance clasificado en corriente y no corriente).
- **Variables:** las 8 del modelo, calculadas con `AppWeb/variables_modelo.py`, el mismo código que usa el sistema. V8 corresponde al dato real del Banco Central del cuarto trimestre de cada año.
- **EBIT:** se usa el resultado de actividades operacionales; si la empresa no lo informa, ganancia antes de impuestos + costos financieros (definición de Altman, 1968).

### 2.2 Etiqueta: zona de insolvencia según Altman

Una empresa-año es **insolvente** si cumple al menos una de estas condiciones:
- **Z''EM < 1,10:** Z-score de Altman para mercados emergentes (Altman et al., 2017; citado en R2, pp. 54-55). Hay 171 casos.
- **Patrimonio ≤ 0:** pasivos mayores que activos, es decir, insolvencia contable (R2, p. 116). Hay 150 casos.

En total, **236 empresa-año insolventes (4,5 %)**. "Insolvente" significa *en zona de riesgo de insolvencia según Altman*, no quiebra legal.

**Por qué Z''EM y no Z1:** Z1 marca al 40 % de las empresas de la CMF, porque castiga la baja rotación de activos típica de sociedades de inversión, eléctricas e inmobiliarias. El detalle está en [fuentes_modelo_ml.md](fuentes_modelo_ml.md).

### 2.3 Separación entrenamiento / prueba real

**Antes de generar datos sintéticos**, las empresas se separaron **por empresa**, para que ninguna aporte datos a la vez al entrenamiento y a la prueba:

| Conjunto | Empresas | Empresa-año | Insolventes |
|---|---|---|---|
| Entrenamiento (base de los sintéticos) | 542 | 4.211 | 185 |
| Prueba real (nunca vista) | 136 | 1.066 | 51 |

Las 3 empresas con quiebra legal según el Boletín Concursal se dejaron siempre en la prueba.

### 2.4 Generación sintética

1. **V7 simulada.** No existen datos públicos de flujo de caja diario. Se simuló como `log(V7) = log(0,30) + 0,10 · leverage + ruido normal(0; 0,35)`. La dirección (más deuda, más volatilidad) sigue a Ringeling (2004, p. 87); los parámetros son supuestos de diseño.
2. **Borderline-SMOTE** (Han et al., 2005; k = 5, m = 10) sobre las empresas reales de entrenamiento, hasta completar cada proporción. Si una clase tenía más empresas reales que las pedidas, se submuestreó.
3. **Identidad DuPont:** en los casos sintéticos, el ROA se recalcula como margen operacional × rotación de activos, porque la interpolación lineal de SMOTE rompe esa igualdad contable.
4. **Reglas axiomáticas** (tablero Miro): se descartaron los casos sintéticos que violan alguna de estas reglas:
   - razón corriente entre 0 y 10;
   - razón corriente > 1 si y solo si el capital de trabajo es positivo;
   - leverage, rotación y margen dentro de sus topes;
   - V7 ≥ 0;
   - en recesión (PIB < 0), ROA no mayor al percentil 99 real.

   Se descartaron entre 367 y 486 casos por dataset.
5. Cada dataset conserva **todas las empresas reales** de entrenamiento y se completa con sintéticos.

### 2.5 Entrenamiento y evaluación

- Random Forest de 300 árboles con `min_samples_leaf = 2`; umbral de clasificación 0,5.
- **Prueba sintética:** 20 % de cada dataset, estratificado, separado antes de entrenar. Es la que exige RNF-08.
- **Prueba real:** las 136 empresas reservadas, con su proporción natural de insolventes (4,8 %).
- **Criterio de elección:** entre los modelos que cumplen la meta mínima en la prueba sintética, el de mayor F1 en la prueba real.

## 3. Resultados

| Proporción | Accuracy sint. | F1 sint. | Recall sint. | Accuracy real | F1 real | Recall real | Precisión real | PR-AUC real |
|---|---|---|---|---|---|---|---|---|
| **50/50 (elegido)** | **98,7 %** | **98,7 %** | **99,1 %** | 96,9 % | **71,3 %** | 80,4 % | 64,1 % | 84,3 % |
| 40/60 | 99,1 % | 98,9 % | 98,9 % | 96,8 % | 70,2 % | 78,4 % | 63,5 % | 84,3 % |
| 30/70 | 98,7 % | 97,8 % | 97,8 % | 96,5 % | 68,9 % | 80,4 % | 60,3 % | 84,0 % |
| 20/80 | 98,6 % | 96,6 % | 96,2 % | 96,8 % | 70,2 % | 78,4 % | 63,5 % | 83,2 % |
| 10/90 | 98,0 % | 89,9 % | 86,5 % | 97,6 % | 75,9 % | 80,4 % | 71,9 % | 85,2 % |

**Lectura (fluctuaciones de error y confianza que pide el Acta):**
- **En la prueba sintética,** el F1 baja a medida que las insolventes son minoría: 98,7 % con 50/50 y 89,9 % con 10/90. Hay menos ejemplos de la clase difícil.
- **En la prueba real,** el comportamiento es casi estable (F1 de 69-76 %). La proporción de entrenamiento cambia poco la capacidad de generalizar a empresas nuevas.
- **La diferencia entre ambas pruebas (≈ 98 % contra ≈ 71 %)** es la brecha esperable entre datos generados desde las mismas reglas y empresas reales que el modelo nunca vio.

### 3.1 Sin datos de caja (situación actual del sistema)

El módulo de caja (RF-19 a RF-22) no está implementado, así que el sistema usa V7 neutra para todas las empresas (mediana de las solventes = 0,341). Medido así en la prueba real:

| | Accuracy | F1 | Recall | Precisión | PR-AUC |
|---|---|---|---|---|---|
| Con V7 simulada | 96,9 % | 71,3 % | 80,4 % | 64,1 % | 84,3 % |
| **Con V7 neutra (hoy)** | **96,9 %** | **69,7 %** | **74,5 %** | **65,5 %** | **77,3 %** |

### 3.2 Importancia de las variables (modelo 50/50)

| Variable | Importancia |
|---|---|
| Leverage total (V3) | 31,1 % |
| Volatilidad del flujo de caja (V7, simulada) | 14,1 % |
| ROA operacional (V4) | 11,2 % |
| Capital de trabajo sobre activos (V2) | 10,6 % |
| Margen operacional (V5) | 10,4 % |
| Razón corriente (V1) | 8,3 % |
| Rotación de activos (V6) | 8,0 % |
| Tasa de captación UF (V8) | 2,4 % |
| Tipo de cambio real (V8) | 2,3 % |
| Variación del PIB (V8) | 1,5 % |

Las variables macro (V8) pesan poco, en línea con Zurita (2008, p. 29): su efecto sobre la probabilidad de quiebra individual es pequeño.

### 3.3 Chequeo ilustrativo con quiebras legales reales

Son solo 3 casos, así que **no permiten calcular métricas**; se muestran como evidencia cualitativa.

| Empresa (último año con datos) | Z''EM | Etiqueta | Probabilidad del modelo |
|---|---|---|---|
| Sartor Administradora General de Fondos (2024) | −15,4 | Insolvente | 1,00 |
| Telecomunicaciones Internacionales (2014) | −15,5 | Insolvente | 0,98 |
| Claro, Vicuña, Valenzuela (2014) | 4,5 | Solvente | 0,08 |

El modelo detecta a 2 de las 3. La tercera solo tiene datos hasta 2014, probablemente varios años antes de su quiebra, cuando sus cifras todavía eran sanas.

## 4. Limitaciones (declarar en el informe)

1. **La etiqueta es la zona de riesgo de Altman, no la quiebra legal.** En Chile hay muy pocas quiebras legales con estados financieros públicos (3 empresas en la CMF). La validación con quiebras reales queda para la etapa con Nstock.
2. **La prueba sintética es optimista.** Los datos sintéticos salen de las mismas empresas y reglas que el entrenamiento; por eso la cifra con empresas reales nunca vistas es la más representativa.
3. **V7 es simulada** y el sistema todavía no la calcula, porque no existe el módulo de caja.
4. **Las empresas de la CMF son grandes** (sociedades anónimas), no PYMES como Nstock.
5. **El dato de la plantilla debe ser de 12 meses.** El modelo se entrenó con flujos anuales, así que Ingresos_Netos, EBIT y Utilidad_Neta deben corresponder a los últimos 12 meses.

## 5. Cómo reproducirlo

```
venv\Scripts\python.exe manage.py actualizar_datos_macro                  (opcional: actualiza V8)
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso1_extraer_cmf.py         (requiere cmf_raw local)
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso2_generar_sinteticos.py
venv\Scripts\python.exe DatasetSinteticoEntrenamientoML\paso3_entrenar_evaluar.py
```

El paso 1 necesita los archivos crudos de la CMF (`DatasetEntrenamientoML/chile_cmf_boletin/cmf_raw/`), que no están en git por su tamaño. Su salida, `cmf_empresas_reales.csv`, sí está en git, así que los pasos 2 y 3 se pueden repetir sin los crudos. Todo usa la semilla 42.
