<div align="center">

# 📊 SmartFinanzas
### Plataforma Transaccional de Liquidez Financiera y Analítica Predictiva de Crisis en PYMES

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x%20/%206.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-1.5+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Proyecto de Título – Ingeniería en Informática · INACAP La Serena**  
*Profesor Guía:* Carlos Covarrubias Astudillo | *Equipo Lostics:* Ignacio Pozo Pozo & Arturo Quiroga Tello  
*Organización Validadora:* Nstock Importaciones (La Serena, Chile)

</div>

---

## 📑 Tabla de Contenido
1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Arquitectura Modular del Sistema](#arquitectura-modular-del-sistema)
3. [Módulos y Características Principales](#módulos-y-características-principales)
4. [Pipeline ETL y Transformación IFRS / CMF](#pipeline-etl-y-transformación-ifrs--cmf)
5. [Motor Predictivo y Catálogo de Recomendaciones a 90 Días](#motor-predictivo-y-catálogo-de-recomendaciones-a-90-días)
6. [Gobernanza Jurídica y Verificación de Casillas Obligatorias](#gobernanza-jurídica-y-verificación-de-casillas-obligatorias)
7. [Instalación y Despliegue Local](#instalación-y-despliegue-local)
8. [Documentación Técnica Especializada](#documentación-técnica-especializada)
9. [Autores y Agradecimientos](#autores-y-agradecimientos)

---

## <a id="descripción-del-proyecto"></a>1. Descripción del Proyecto

**SmartFinanzas** es una plataforma web desarrollada en Python y Django orientada a mitigar la brecha operativa y analítica que enfrentan las Pequeñas y Medianas Empresas (PYMES) chilenas frente al riesgo de asfixia financiera e insolvencia.

A diferencia de las herramientas convencionales como planillas Excel o tableros de BI (que únicamente describen el pasado de forma retrospectiva), SmartFinanzas implementa un **enfoque predictivo y prescriptivo de ciencia aplicada**:
* **Pipeline ETL Inteligente:** Ingesta y valida rigurosamente balances contables en formatos `.xlsx` y `.csv` exportados desde sistemas ERP (como Facto) o la CMF, normalizando nomenclaturas IFRS y verificando la ecuación patrimonial antes de cualquier cálculo.
* **Ingeniería Financiera Desacoplada:** Transforma los estados financieros en un vector de **7 variables adimensionales** ($X_1$ a $X_7$) respaldadas en literatura chilena e internacional (Altman, Zurita, Ringeling, Riquelme).
* **Motor Predictivo de Machine Learning:** Clasificador *Random Forest* entrenado sobre estados financieros reales reportados ante la Comisión para el Mercado Financiero (CMF), capaz de inferir la probabilidad de insolvencia para los próximos 90 días ($Q_t \to Q_{t+1}$) con explicabilidad local **SHAP**.
* **Planes de Acción Preventivos:** Catálogo de recomendaciones financieras en **Lenguaje Ejecutivo Accesible** (*Business Plain Spanish*), que prescribe qué medidas operativas concretas debe adoptar la gerencia para mitigar el deterioro o consolidar la solvencia.

> [!NOTE]
> El proyecto está validado funcionalmente con la empresa distribuidora mayorista **Nstock Importaciones** (La Serena, Chile).

---

## <a id="arquitectura-modular-del-sistema"></a>2. Arquitectura Modular del Sistema

El proyecto está diseñado bajo un patrón arquitectónico de **Monolito Modular Desacoplado**, donde la ingesta contable, la capa analítica de inferencia y la gestión transaccional operan con estricta separación de responsabilidades:

```text
SmartFinanzas/
│
├── SmartFinanzas/                     # Configuración central del proyecto Django
│   ├── settings.py                    # Configuración global (Apps, Base de datos MySQL, Auth)
│   ├── urls.py                        # Enrutador principal de URLs
│   ├── asgi.py                        # Entrada ASGI
│   └── wsgi.py                        # Entrada WSGI
│
├── moduloETL/                         # Motor de Ingesta, Parseo y Normalización Contable
│   ├── etl_financiero.py              # Procesador OOD en memoria (Pandas/OpenPyXL) sin dependencias de DB
│   ├── services.py                    # Servicios de almacenamiento y cálculo de ratios en base de datos
│   ├── models.py                      # Modelos: CargaFinanciera, Balance, RatioFinanciero
│   ├── forms.py                       # Formulario de carga con control de tamaño (25 MB máx)
│   ├── views.py                       # Vistas: subida de balance, extracción y selección de períodos
│   └── tests_etl_financiero.py        # Suite de pruebas automatizadas del motor ETL
│
├── capaAnalitica/                     # Servicio de Inferencia ML, Explicabilidad y Recomendaciones
│   ├── modelo_oficial/                # Clasificador Random Forest v11 (.joblib) y métricas
│   ├── services.py                    # Servicio de inferencia probabilística y explicabilidad SHAP local
│   ├── catalogo_recomendaciones.py    # Catálogo Maestro: Matriz de 9 transiciones macro y 7 tácticas operativas
│   └── models.py                      # Modelos: PrediccionRiesgo, VariableInfluencia, Recomendacion
│
├── moduloTransaccional/               # Operación Diaria de Caja, Ventas y Arqueos
│   ├── models.py                      # Modelos: Venta, RetiroCajaChica, CierreCaja, MetodoPago
│   ├── forms.py                       # Formularios con cuadratura estricta y justificación obligatoria
│   └── views.py                       # Vistas de registro de ventas, retiros y sellado inmutable de cierre
│
├── dashboard/                         # Interfaz Analítica y Reportes Ejecutivos
│   ├── views.py                       # Controlador del Dashboard General y Dashboard Predictivo a 90 días
│   ├── urls.py                        # Rutas de navegación y endpoint de exportación a PDF
│   └── templates/dashboard/           # Vistas responsivas (Chart.js interactivo con backtesting visual)
│
├── usuarios/                          # Autenticación, Gobernanza y Roles (RBAC)
│   ├── models.py                      # Modelos: Usuario, Rol (Dueño / Contador / Trabajador), Empresa
│   ├── forms.py                       # Formularios de autenticación y registro
│   └── views.py                       # Flujo de login, registro con términos legales y logout
│
├── templates/                         # Plantillas HTML globales y de módulos (Bootstrap 5.3)
│   ├── base.html                      # Layout maestro con navegación lateral y diseño responsivo
│   ├── moduloETL/                     # Vistas de carga de balance y ratios
│   └── moduloTransaccional/           # Vistas de cierre de caja y ventas
│
├── docs/                              # Documentación Técnica, Legal y Metodológica Formal
│   ├── plan_recomendaciones_predictivas.md # Arquitectura del plan de acción y literatura chilena
│   ├── avisos_legales_y_concursales.md     # Marco legal concursal (Ley 20.720/21.563) y responsabilidades
│   ├── transformacion_ifrs_etl.md          # Especificación del pipeline de transformación IFRS
│   └── metodologia_medicion_insolvencia.md # Fundamento científico y formulación matemática
│
├── manage.py                          # Script de gestión de comandos de Django
└── requirements.txt                   # Dependencias del entorno virtual Python
```

---

## <a id="módulos-y-características-principales"></a>3. Módulos y Características Principales

* **Control Transaccional de Caja:** Registro diario de ventas por método de pago (Efectivo, Débito, Crédito, Transferencia), deducción de comisiones, retiros de caja chica y arqueo ciego con **justificación obligatoria de descuadres** (NIA 240 / Código de Comercio).
* **Pipeline ETL Financiero:** Ingesta horizontal de balances con detección automática de cuentas IFRS, conversión defensiva de signos contables y comprobación de la ecuación patrimonial.
* **Dashboard Predictivo a 90 Días:** Monitoreo gráfico de la curva de insolvencia ($Q_t \to Q_{t+1}$), selección dinámica de períodos, matriz de validación histórica retrospectiva (backtesting) y explicabilidad Top 3 SHAP.
* **Plan de Acción Preventivo:** Prescripción gerencial estructurada en 3 niveles (*Situación Actual, Acción Recomendada, Paso a Paso Sugerido*) redactada en Lenguaje Ejecutivo Accesible sin jerga abstracta.
* **Reportería Ejecutiva Oficial:** Generación de informes gerenciales descargables en PDF con sellado temporal y deslinde fiduciario.

---

## <a id="pipeline-etl-y-transformación-ifrs--cmf"></a>4. Pipeline ETL y Transformación IFRS / CMF

El motor `FinancialETLProcessor` homologa la nomenclatura de los estados financieros a través de un diccionario léxico de sinónimos contables (`CANONICAL_SYNONYMS`):
1. **Normalización fonética:** Remoción de acentos, caracteres especiales y conversión a minúsculas sin espacios (`normalize_text`).
2. **Parseo numérico defensivo:** Conversión de paréntesis contables `(monto)` a números negativos, remoción de signos monetarios (`$`, `UF`) y detección adaptativa de separadores de miles y decimales (`clean_number`).
3. **Regla Fallback de EBIT:** Si el balance no detalla el Resultado Operacional, se deduce como:
   $$\text{EBIT} = \text{Ganancia Antes de Impuestos (EBT)} + \text{Costos Financieros}$$
4. **Validaciones Axiomáticas:** Comprobación estricta de Activo Total $> 0$, tolerancia de desbalance patrimonial $\le 5\%$, detección de quiebra técnica (Patrimonio Neto $\le 0$) y coherencia de subcuentas corrientes.
5. **Cálculo de los 7 Ratios Adimensionales ($X_1$ a $X_7$):** Razón Corriente, Capital de Trabajo sobre Activos, Leverage Total, ROA Operacional, Margen Operacional, Rotación de Activos y Volatilidad de Flujo de Caja.

> *Para mayores detalles técnicos, consulte [docs/transformacion_ifrs_etl.md](docs/transformacion_ifrs_etl.md).*

---

## <a id="motor-predictivo-y-catálogo-de-recomendaciones-a-90-días"></a>5. Motor Predictivo y Catálogo de Recomendaciones a 90 Días

El subsistema analítico vincula la probabilidad de insolvencia a la literatura empírica de quiebras en Chile (Zurita 2008, Ringeling 2004, Riquelme 2018 y Ley 20.720):
* **Matriz de Transición Intertemporal ($3 \times 3$):** Evalúa el par $(\text{Score}_{Q_t}, \text{Score}_{Q_{t+1}})$ clasificando el riesgo en tres zonas:
  * **Verde (Solvente):** $Score \le 35\%$
  * **Amarillo (Alerta Preventiva):** $35\% < Score \le 70\%$
  * **Rojo (Riesgo Crítico):** $Score > 70\%$
* **Lenguaje Ejecutivo Accesible:** Diagnósticos cuantitativos traducidos a dinero real cotidiano (*"Por cada $1.000 que debe pagar, dispone de $1.170 en recursos inmediatos..."* o *"El nivel de deuda actual supera en 4.8 veces el patrimonio de los dueños..."*).
* **Persistencia Fiduciaria:** Cada recomendación se almacena en la tabla MySQL `recomendacion` vinculada por Foreign Key unívoca a la clave primaria del período evaluado (`prediccion_id`).

> *Para mayores detalles metodológicos, consulte [docs/plan_recomendaciones_predictivas.md](docs/plan_recomendaciones_predictivas.md).*

---

## <a id="gobernanza-jurídica-y-verificación-de-casillas-obligatorias"></a>6. Gobernanza Jurídica y Verificación de Casillas Obligatorias

El sistema implementa un mecanismo estricto de **control de certificaciones obligatorias**:
* **Bloqueo Visual y Funcional:** En todos los formularios críticos (Carga de Balances, Cierre de Caja, Registro de Usuarios y Descarga de Informes ML), los botones de acción inician en estado **`disabled`**.
* **Condición de Habilitación:** El botón se habilita únicamente cuando el usuario marca de forma voluntaria la casilla de aceptación y certificación legal.
* **Validación en Doble Capa:** Si el usuario desmarca la casilla, el botón se bloquea de inmediato. Además, tanto JavaScript en el frontend (`addEventListener('submit')`) como las vistas Django en el backend (`request.POST.get('terminos_aceptados')`) rechazan cualquier petición que no incluya la certificación explícita.
* **Marco Concursal Chileno (Ley 20.720 y Ley 21.563):** Define las vías de Reorganización Judicial, Reorganización Simplificada para MiPymes, deber de diligencia de administradores y advertencia sobre delitos concursales (insolvencia fraudulenta).

> *Para el estudio jurídico completo de cada módulo y estado de riesgo, consulte [docs/avisos_legales_y_concursales.md](docs/avisos_legales_y_concursales.md).*

---

## <a id="instalación-y-despliegue-local"></a>7. Instalación y Despliegue Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/SmartFinanzas.git
cd SmartFinanzas
```

### 2. Crear y activar el entorno virtual
* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (.env)
Crea un archivo `.env` en la raíz del proyecto configurado para MySQL:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-django
DB_NAME=smartfinanzas3
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```
Accede a la plataforma en tu navegador web mediante:  
`http://127.0.0.1:8000/`

---

## <a id="documentación-técnica-especializada"></a>8. Documentación Técnica Especializada

Para profundizar en la arquitectura, modelos matemáticos y fundamentos jurídicos de la plataforma, consulte los documentos disponibles en el directorio `docs/`:

1. [docs/plan_recomendaciones_predictivas.md](docs/plan_recomendaciones_predictivas.md): Diseño del Plan de Acción a 90 Días, matriz de transición intertemporal y fundamentación empírica en literatura chilena.
2. [docs/avisos_legales_y_concursales.md](docs/avisos_legales_y_concursales.md): Análisis exhaustivo de los avisos legales, deberes de administración, responsabilidad civil/penal y procedimientos de la Ley 20.720 y Ley 21.563 por semáforo de riesgo.
3. [docs/transformacion_ifrs_etl.md](docs/transformacion_ifrs_etl.md): Especificación técnica del pipeline ETL, diccionario de sinónimos contables, validaciones axiomáticas y cálculo de los 7 ratios financieros.
4. [docs/metodologia_medicion_insolvencia.md](docs/metodologia_medicion_insolvencia.md): Formulación matemática del modelo Altman EMS y fundamentación de las variables canónicas.

---

## <a id="autores-y-agradecimientos"></a>9. Autores y Agradecimientos

* **Ignacio Pozo Pozo** – Desarrollo Fullstack, Ingeniería de Datos & Machine Learning.
* **Arturo Quiroga Tello** – Gestión de Proyecto, Desarrollo Fullstack, Testing & QA.
* **Carlos Covarrubias Astudillo** – Docente Guía y Asesoría Metodológica.
* **Juan Pablo Yáñez Riquelme** – Docente Consultor y Asesor Técnico en Machine Learning.
* **Alexis Vázquez & Natalia Pezoa** – Representantes de *Nstock Importaciones* (Validación Operativa y Pruebas de Campo).
* **INACAP Sede La Serena** – Área de Tecnologías de Información y Ciberseguridad.

---
*SmartFinanzas – Innovación analítica y tecnológica aplicada a la preservación de la solvencia empresarial.*
