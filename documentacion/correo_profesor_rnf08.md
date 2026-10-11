Asunto: Consulta urgente RNF-08 — resultados con Chile y Colombia, necesito su decisión para avanzar

Estimado profesor Covarrubias,

Le escribo porque llegamos a un punto donde necesitamos su decisión para poder seguir avanzando con el informe — la plantilla exige evidencia de viabilidad técnica documentada, y no queremos seguir invirtiendo tiempo en una línea que después no sea aceptable para la evaluación.

**Resumen de lo que hicimos:**

1. **Con los 6 datasets extranjeros probados hasta ahora** (Taiwan, Polish, American, Russian, HAT China, SMEsD, Slovak), el techo de F1 encontrado tras 17+ configuraciones (modelos, resampling, ingeniería de features) es de **~44-49%**, muy por debajo del 80% del RNF-08. La causa confirmada es el desbalance estructural de la clase minoritaria (quiebras reales son 3-7% de los datos), no la cantidad de datos ni el algoritmo. El modelo en producción hoy (Taiwan + RandomForest) da F1 46.8%.

2. **Intentamos construir un dataset 100% chileno** cruzando por RUT los estados financieros públicos de la CMF (912 empresas, 2009-2024) con el Boletín Concursal (3.149 empresas en Liquidación desde 2014). La intersección dio **solo 3 empresas** con datos completos. Con esos 3 casos igual intentamos entrenar/validar y el resultado fue F1=0% de forma consistente en 20 corridas distintas — confirma empíricamente que n=3 no es entrenable.

3. **Ante la escasez de datos chilenos, buscamos otro país hispanohablante para reducir el sesgo geográfico** que usted mencionó como preocupación. Encontramos que **Colombia (Superintendencia de Sociedades)** sí publica en abierto tanto el listado de empresas en insolvencia (7.477 NIT, 2019-2025) como los estados financieros NIIF de miles de empresas (incluyendo PYMEs). Cruzando ambas fuentes construimos un dataset real de **9.439 empresas colombianas** (3.429 con quiebra confirmada + 6.010 sanas) — muy superior en volumen al de Chile.

4. **Con Colombia probamos varias metodologías, siendo rigurosos en no inflar el resultado artificialmente:**
   - Entrenando y evaluando con la proporción de quiebras tal como se descargó (36%): F1 73.7% — mostramos que este número es engañoso, porque no refleja la tasa real de quiebra (~3%).
   - Entrenando con todos los positivos disponibles pero evaluando con la proporción real de quiebra (3.2%, igual que Taiwan): **F1 26.0%**.
   - Probamos 3 algoritmos distintos (RandomForest, BalancedRandomForest, EasyEnsemble — el que mejor resultado dio con Taiwan): ninguno mejoró significativamente el resultado anterior.
   - Corregimos un problema metodológico (usar solo estados financieros de **antes** de que la empresa entrara en insolvencia, no durante o después): esto subió el resultado a **F1 29.4%**, con una metodología más defendible, pero seguimos por debajo de Taiwan.

**Conclusión con evidencia empírica de 3 países:**

| Dataset | F1 (prevalencia real ~3%) |
|---|---|
| Taiwan (producción actual) | 46.8% |
| Colombia (periodo corregido, mejor resultado) | 29.4% |
| Chile (n=3, no entrenable) | 0% |

Probamos con todo lo que tuvimos a mano — datasets extranjeros, la ruta chilena, y una segunda ruta hispanohablante (Colombia) con volumen real — y en ningún caso nos acercamos al 80% del RNF-08. Todo el proceso, scripts y resultados quedan documentados en `DatasetEntrenamientoML/busqueda_mejora_f1.md` y en las carpetas `chile_cmf_boletin/` y `colombia_supersociedades/` del repositorio, por si quiere revisar el detalle.

**Nuestra consulta concreta:**

Dado que usted mencionó que usar datos de otro país podría introducir sesgo geográfico, y que efectivamente Colombia dio peor resultado que Taiwan (no mejor), ¿cómo prefiere que avancemos?

- (a) ¿Nos quedamos con el modelo actual (Taiwan, F1 ~47-49%) y renegociamos el umbral del RNF-08, documentando ambos intentos (Chile y Colombia) como evidencia de la limitación de datos disponibles?
- (b) ¿Prefiere que sigamos intentando mejorar Colombia (por ejemplo, buscando más años de historia financiera por empresa) antes de cerrar esta línea?
- (c) ¿Alguna otra alternativa que usted recomiende?

Necesitamos su decisión para poder seguir con el resto del informe, ya que la plantilla exige que la sección de viabilidad técnica y el RNF-08 queden con un valor definido y respaldado. Quedamos atentos a su respuesta.

Saludos cordiales,
Ignacio Pozo
Equipo Lostics — SmartFinanzas
