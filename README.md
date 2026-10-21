<div align="center">

# 📊 SmartFinanzas
### Plataforma Transaccional de Liquidez Financiera y Analítica Predictiva de Crisis en PYMES

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x%20/%206.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-1.5+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Proyecto de Título – Ingeniería en Informática · INACAP La Serena**  
*Profesor Guía:* Carlos Covarrubias Astudillo | *Equipo Lostics:* Ignacio Pozo Pozo & Arturo Quiroga Tello  
*Organización Validadora:* Nstock Importaciones (La Serena, Chile)

</div>

---

## 📑 Tabla de Contenido
1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Arquitectura Tecnológica y Estructura del Sistema](#arquitectura-tecnológica-y-estructura-del-sistema)
3. [Características Principales](#características-principales)
4. [Modelo Predictivo y Fundamento Científico](#modelo-predictivo-y-fundamento-científico)
5. [Instalación y Despliegue Local](#instalación-y-despliegue-local)
6. [Guía de Uso por Roles](#guía-de-uso-por-roles)
7. [Plan de Pruebas y Aseguramiento de Calidad](#plan-de-pruebas-y-aseguramiento-de-calidad)
8. [Cumplimiento Normativo y Seguridad](#cumplimiento-normativo-y-seguridad)
9. [Autores y Agradecimientos](#autores-y-agradecimientos)

---

## <a id="descripción-del-proyecto"></a> Descripción del Proyecto

**SmartFinanzas** es una plataforma web desarrollada en Python y Django orientada a mitigar la brecha operativa y analítica que enfrentan las Pequeñas y Medianas Empresas (PYMES) chilenas frente al riesgo de insolvencia y asfixia financiera.

A diferencia de las herramientas convencionales como planillas Excel o tableros de BI (que únicamente describen el pasado de forma reactiva), SmartFinanzas implementa un **enfoque predictivo de ciencia aplicada**:
* **Pipeline ETL Inteligente:** Ingesta y valida rigurosamente balances contables en formatos `.xlsx` y `.csv` exportados desde sistemas ERP (como Facto), comprobando la ecuación patrimonial y consistencia matemática antes de cualquier cálculo.
* **Ingeniería Financiera Desacoplada:** Transforma los estados financieros en un vector de **7 variables adimensionales** (V_1 a V_7) respaldadas en literatura académica chilena e internacional (Altman, Riquelme, Zurita, Ringeling).
* **Motor Predictivo de Machine Learning (Modelo Oficial v11):** Clasificador *Random Forest* entrenado exclusivamente con estados financieros reales de empresas chilenas reportados ante la Comisión para el Mercado Financiero (CMF), capaz de inferir la probabilidad de insolvencia con semáforos de alerta temprana y un módulo de **explicabilidad transparente** que expone las causas del riesgo financiero.

> [!NOTE]
> El proyecto está validado funcionalmente con la empresa distribuidora mayorista **Nstock Importaciones** (La Serena, Chile).

---

## <a id="arquitectura-tecnológica-y-estructura-del-sistema"></a> Arquitectura Tecnológica y Estructura del Sistema

El proyecto está diseñado bajo un patrón arquitectónico en Django modular y desacoplado, donde la lógica de ratios contables y el motor analítico de Machine Learning operan de forma independiente de la base de datos y la interfaz gráfica.

### Estructura del Repositorio

```text
SmartFinanzas/
│
├── SmartFinanzas/                     # Configuración principal del proyecto Django
│   ├── settings.py                    # Configuración global (Apps, Base de datos SQLite3, Auth)
│   ├── urls.py                        # Enrutador principal de URLs
│   ├── asgi.py                        # Entrada ASGI para despliegues asíncronos
│   └── wsgi.py                        # Entrada WSGI para servidores de producción
│
├── AppWeb/                            # Aplicación principal del sistema
│   ├── migrations/                    # Control de versiones del esquema de base de datos
│   ├── modelo_oficial/                # Artefactos ML preentrenados y serializados
│   │   ├── modelo_riesgo_v11.joblib   # Clasificador Random Forest oficial v11 (Joblib)
│   │   └── metricas_v11.joblib        # Métricas de validación en prueba real no vista
│   ├── templates/AppWeb/              # Plantillas HTML (Bootstrap 5 + Chart.js)
│   │   ├── base.html                  # Plantilla base y diseño responsivo
│   │   ├── index.html                 # Tablero principal de control
│   │   ├── cargaDatos.html            # Interfaz de carga masiva ETL para el Contador
│   │   ├── resultado_prediccion.html  # Panel de resultados, semáforo, top 3 y gráficos
│   │   ├── resultado_prediccion_pdf.html # Plantilla para exportación a PDF
│   │   ├── login.html                 # Autenticación de usuarios
│   │   └── registro.html              # Registro con asignación de rol (Dueño / Contador)
│   ├── admin.py                       # Configuración del panel de administración Django
│   ├── apps.py                        # Registro y metadatos de la aplicación AppWeb
│   ├── decorators.py                  # Decorador @rol_requerido para control de acceso (RBAC)
│   ├── models.py                      # Modelos ORM: PerfilUsuario, EstadoCarga, Empresa, HistorialPrediccion
│   ├── urls.py                        # Rutas y endpoints internos de la app
│   ├── variables_modelo.py            # Fórmulas de las 7 variables adimensionales (puro Python desacoplado)
│   ├── views.py                       # Vistas: flujo de autenticación, ETL de carga, predicción y PDF
│   ├── viewsML.py                     # Motor analítico: inferencia ML, explicabilidad y recomendaciones
│   └── tests.py                       # Suite automatizada de pruebas unitarias e integración (11 tests)
│
├── DatasetEntrenamientoML/            # Datasets base y experimentos previos (CMF, quiebras internacionales)
│
├── DatasetSinteticoEntrenamientoML/   # Pipeline de datos y scripts del modelo oficial v11
│   ├── paso1_extraer_cmf.py           # Extracción y filtrado de estados financieros IFRS de la CMF
│   ├── paso2_generar_sinteticos.py    # Generación y validación comparativa de sintéticos
│   ├── paso3_entrenar_evaluar.py      # Script de entrenamiento y evaluación oficial del modelo
│   └── paso4_analisis_tamano.py       # Análisis de desempeño segregado por tamaño de empresa (PYME vs Grande)
│
├── PlantillasPrueba/                  # Archivos .csv y .xlsx de balance para pruebas funcionales y masivas
│
├── documentacion/                     # Documentación técnica, bitácoras de entrenamiento y arquitectura
│   ├── ARCHITECTURE.md                # Diagramas y detalles de la arquitectura de software
│   ├── SETUP_WINDOWS.md               # Guía paso a paso para entorno Windows
│   ├── SETUP_LINUX.md                 # Guía paso a paso para entorno Linux
│   ├── resultados_entrenamiento_v11.md# Reporte formal de métricas del modelo oficial v11
│   └── fuentes_modelo_ml.md           # Respaldo bibliográfico y justificación matemática de variables
│
├── manage.py                          # Script de gestión de comandos de Django
├── requirements.txt                   # Lista de dependencias del entorno Python
└── db.sqlite3                         # Base de datos local SQLite (autogenerada)
```

---

## <a id="características-principales"></a>Características Principales

* **Control Transaccional de Caja:** Registro diario de ventas desglosado por método de pago (Efectivo, Débito, Crédito, Transferencia), deducción automática de comisiones de adquirencia, gestión de retiros de caja chica y arqueo con justificación obligatoria de descuadres.
* **Proceso ETL Robusto:** Validación sintáctica de archivos `.xlsx` y `.csv` importados desde sistemas ERP (como ERP Facto), previniendo nulos, errores de tipo y descuadres contables antes del procesamiento analítico.
* **Motor Predictivo con Explicabilidad:** Generación de un score de riesgo ($0$ a $100$) clasificado en un semáforo de tres niveles (Verde, Amarillo, Rojo), complementado con un panel que expone las tres variables de mayor impacto en la predicción.
* **Recomendaciones Automatizadas:** Emisión de pautas de gestión financiera orientadas a corregir el vector de riesgo detectado.
* **Reportería Ejecutiva:** Exportación de informes gerenciales completos en formato PDF (`ReportLab`).

---

## <a id="modelo-predictivo-y-fundamento-científico"></a>Modelo Predictivo y Fundamento Científico

El clasificador supervisado se fundamenta en un vector de **7 variables adimensionales** rigurosamente depuradas para el ecosistema PYME, evitando sesgos de escala e incongruencias tributarias:

| ID | Variable / Feature | Categoría | Rol en la Detección Temprana |
| :--- | :--- | :--- | :--- |
| **V1** | **Razón Corriente** | Liquidez Inmediata | Cobertura de compromisos exigibles a corto plazo. |
| **V2** | **Capital de Trabajo / Activos** | Liquidez Estructural | Magnitud del colchón de maniobra normalizado. |
| **V3** | **Leverage Total** | Endeudamiento | Nivel de compromiso patrimonial frente a terceros. |
| **V4** | **ROA Operacional** | Rentabilidad | Productividad bruta del activo total. |
| **V5** | **Margen Operacional** | Eficiencia de Costos | Cojín de rentabilidad por cada peso vendido. |
| **V6** | **Rotación de Activos** | Eficiencia de Activos | Dinamismo comercial y control de inmovzbilización. |
| **V7** | **Volatilidad del Flujo** | Volatilidad Diaria | Riesgo estocástico de asfixia por caja (Merton / Zurita). |

* **Estrategia de Entrenamiento:** Entrenado sobre estados financieros IFRS de la CMF (2012–2024) etiquetados mediante la zona de riesgo del modelo Altman $Z''_{EM} < 1.10$ o patrimonio negativo. 
* **Mitigación de Desbalance:** Uso de *Borderline-SMOTE* y filtrado estricto mediante una **matriz de reglas axiomáticas** en Pandas/NumPy para anular registros sintéticos contablemente inviables.
* **Métricas de Evaluación:** Optimización centrada en la clase minoritaria mediante PR-AUC ($\ge 80\%$), Recall ($\ge 70\%$) y F1-score ($\ge 70\%$).

---

## <a id="instalación-y-despliegue-local"></a>Instalación y Despliegue Local

Sigue estos pasos para clonar y poner en marcha el entorno de desarrollo:

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
  *(Si PowerShell restringe la ejecución de scripts, ejecuta: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*
* **En Windows (CMD):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
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

### 4. Configurar variables de entorno y base de datos
Crea un archivo `.env` en la raíz del proyecto basándote en el entorno de MySQL configurado:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-django
DB_NAME=smartfinanzas_db
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_HOST=localhost
DB_PORT=3306
```

### 5. Aplicar migraciones y poblar datos iniciales
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data.json  # Roles y métodos de pago base
  ```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```
Accede a la plataforma en tu navegador mediante `http://127.0.0.1:8000/`.

---

## <a id="guía-de-uso-por-roles"></a>Guía de Uso por Roles

El sistema implementa control de acceso basado en roles:
1. **Dueño (Gerente General):** Opera el módulo transaccional de caja (registra retiros de caja chica, ejecuta el cierre diario y justifica descuadres), consulta el Dashboard analítico y toma decisiones preventivas.
2. **Trabajador:** Registra las ventas diarias con sus respectivos métodos de pago y aplica descuentos manuales autorizados.
3. **Contador (Externo):** Realiza la carga de las planillas financieras exportadas desde ERP Facto, valida la tabla de ratios calculados por el ETL y ejecuta la inferencia del motor predictivo.
4. **Administrador:** Gestiona cuentas de usuario, asignación de roles y parámetros generales de la empresa en el panel de control.

---

## <a id="plan-de-pruebas-y-aseguramiento-de-calidad"></a>Plan de Pruebas y Aseguramiento de Calidad

* **Pruebas Unitarias e Integración:** Ejecución de la suite automatizada con `Pytest`:
```bash
  pytest --cov=. --cov-report=html
  ```
* **Pruebas de Carga y Rendimiento:** Verificación de tiempos de respuesta (< 3 segundos) mediante simulaciones concurrentes con **Apache JMeter**.
* **Auditoría de Seguridad:** Validación nativa de Django contra vulnerabilidades OWASP Top 10 (Inyección SQL, XSS, CSRF) y cumplimiento estricto de cifrado en tránsito HTTPS/TLS.

---

## <a id="cumplimiento-normativo-y-seguridad"></a>Cumplimiento Normativo y Seguridad

* **Protección de Datos:** Diseñado en estricto cumplimiento con la **Ley 19.628** sobre Protección de la Vida Privada y adaptado a las exigencias de gobernanza de la **Ley 21.719** (Agencia de Protección de Datos Personales).
* **Calidad de Software:** Alineado con las dimensiones prioritarias del estándar internacional **ISO/IEC 25010** (Seguridad, Usabilidad, Mantenibilidad y Fiabilidad).

---

## <a id="autores-y-agradecimientos"></a>Autores y Agradecimientos

* **Ignacio Pozo Pozo** – Desarrollo Fullstack, Ingeniería de Datos & Machine Learning.
* **Arturo Quiroga Tello** – Gestión de Proyecto, Desarrollo Fullstack, Testing & QA.
* **Carlos Covarrubias Astudillo** – Docente Guía y Asesoría Metodológica.
* **Juan Pablo Yáñez Riquelme** – Docente Consultor y Asesor Técnico en Machine Learning.
* **Alexis Vázquez & Natalia Pezoa** – Representantes de *Nstock Importaciones* (Validación Operativa y Pruebas de Campo).
* **INACAP Sede La Serena** – Espacio CreaEmpresas y Dirección Académica del Área de Tecnologías de Información.

---
*SmartFinanzas – Desarrollado con fines profesionales e innovación tecnológica aplicada al ecosistema PYME.*
