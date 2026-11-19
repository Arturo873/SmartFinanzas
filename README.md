<div align="center">

# 📊 SmartFinanzas
### Plataforma Transaccional de Liquidez Financiera y Analítica Predictiva de Crisis en PYMES

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2_LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-1.5+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0_/_MariaDB-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
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
2. [Arquitectura Tecnológica y Estructura Modular](#arquitectura-tecnológica-y-estructura-modular)
3. [Módulos y Características Principales](#módulos-y-características-principales)
4. [Pipeline ETL y Normalización IFRS / CMF](#pipeline-etl-y-normalización-ifrs--cmf)
5. [Modelo Predictivo de Machine Learning y Fundamento Científico](#modelo-predictivo-y-fundamento-científico)
6. [Dashboard Analítico y Plan de Acción a 90 Días](#dashboard-analítico-y-plan-de-acción-a-90-días)
7. [Control de Acceso y Guía de Uso por Roles (RBAC)](#control-de-acceso-y-guía-de-uso-por-roles-rbac)
8. [Gobernanza Jurídica y Certificación Concursal](#gobernanza-jurídica-y-certificación-concursal)
9. [Instalación y Despliegue Local](#instalación-y-despliegue-local)
10. [Aseguramiento de Calidad y Pruebas](#aseguramiento-de-calidad-y-pruebas)
11. [Cumplimiento Normativo y Seguridad](#cumplimiento-normativo-y-seguridad)
12. [Documentación Técnica y Legal de Respaldo](#documentación-técnica-y-legal-de-respaldo)
13. [Autores y Agradecimientos](#autores-y-agradecimientos)

---

## <a id="descripción-del-proyecto"></a>1. Descripción del Proyecto

**SmartFinanzas** es una plataforma web desarrollada en Python y Django orientada a mitigar la brecha operativa y analítica que enfrentan las Pequeñas y Medianas Empresas (PYMES) chilenas frente al riesgo de insolvencia y asfixia financiera.

A diferencia de las herramientas convencionales como planillas Excel o tableros de BI (que únicamente describen el pasado de forma reactiva), SmartFinanzas implementa un **enfoque predictivo y prescriptivo de ciencia aplicada**:
* **Pipeline ETL Inteligente:** Ingesta y normaliza balances contables en formatos `.xlsx` y `.csv` exportados desde sistemas ERP (como Facto) o la CMF, verificando rigurosamente la ecuación patrimonial y consistencia matemática antes de cualquier cálculo.
* **Ingeniería Financiera Desacoplada:** Transforma los estados financieros en un vector de **7 variables adimensionales** ($V_1$ a $V_7$) respaldadas en literatura académica chilena e internacional (Altman, Zurita, Ringeling, Riquelme).
* **Motor Predictivo de Machine Learning (Modelo Oficial v11):** Clasificador *Random Forest* entrenado con estados financieros reales reportados ante la Comisión para el Mercado Financiero (CMF), capaz de inferir la probabilidad de insolvencia para los próximos 90 días ($Q_t \to Q_{t+1}$) con explicabilidad local **SHAP**.
* **Planes de Acción Preventivos:** Catálogo de recomendaciones financieras en **Lenguaje Ejecutivo Accesible** (*Business Plain Spanish*), que prescribe qué medidas operativas concretas debe adoptar la gerencia para mitigar el deterioro o consolidar la solvencia.

> [!NOTE]
> El proyecto está validado funcional y operativamente con la empresa distribuidora mayorista **Nstock Importaciones** (La Serena, Chile).

---

## <a id="arquitectura-tecnológica-y-estructura-modular"></a>2. Arquitectura Tecnológica y Estructura Modular

El proyecto está diseñado bajo un patrón arquitectónico de **Monolito Modular Desacoplado**, donde la ingesta contable, la capa analítica de inferencia, la gestión transaccional y la autenticación operan con estricta separación de responsabilidades y cero acoplamiento indebido de base de datos en los motores de cálculo en memoria.

### Estructura del Repositorio

```text
SmartFinanzas/
│
├── SmartFinanzas/                     # Configuración central del proyecto Django
│   ├── settings.py                    # Configuración global (Apps, Base de datos MySQL/MariaDB, Auth)
│   ├── urls.py                        # Enrutador principal de URLs y redirecciones
│   ├── asgi.py                        # Entrada ASGI para despliegues asíncronos
│   └── wsgi.py                        # Entrada WSGI para servidores de producción
│
├── moduloETL/                         # Motor de Ingesta, Parseo y Normalización Contable
│   ├── etl_financiero.py              # Procesador OOD en memoria (FinancialETLProcessor) sin dependencias de DB
│   ├── services.py                    # Almacenamiento, auditoría y persistencia de ratios calculados
│   ├── models.py                      # Modelos: FinancialUpload, FinancialStatement, FinancialRatio
│   ├── forms.py                       # Formulario de carga con control de tamaño y validación IFRS
│   ├── views.py                       # Vistas: subida de balance, matriz de ratios e historial de cargas
│   ├── tests.py                       # Pruebas de integración del módulo ETL
│   └── tests_etl_financiero.py        # Suite de pruebas unitarias automatizadas del motor ETL
│
├── capaAnalitica/                     # Servicio de Inferencia ML, Explicabilidad y Recomendaciones
│   ├── modelo_oficial/                # Clasificador Random Forest v11 (.joblib) y métricas de validación
│   ├── services.py                    # Inferencia probabilística, explicabilidad SHAP y scoring a 90 días
│   ├── catalogo_recomendaciones.py    # Matriz de 9 transiciones macro y 7 tácticas operativas en Business Plain Spanish
│   ├── models.py                      # Modelos: RiskPrediction, VariableInfluence, Recommendation
│   └── tests.py                       # Pruebas del motor predictivo y catalogo de recomendaciones
│
├── moduloTransaccional/               # Operación Diaria de Caja, Ventas y Arqueos
│   ├── models.py                      # Modelos: Venta, RetiroCajaChica, CierreCaja, MetodoPago
│   ├── forms.py                       # Formularios con cuadratura estricta y justificación obligatoria
│   ├── views.py                       # Vistas de registro de ventas POS, retiros y sellado inmutable de cierre
│   └── tests.py                       # Pruebas de validación transaccional y cuadratura de caja
│
├── dashboard/                         # Interfaz Analítica y Reportes Ejecutivos
│   ├── views.py                       # Controladores: Tablero Actual y Tablero Predictivo a 90 días
│   ├── pdf_generator.py               # Generación y exportación de informes gerenciales PDF (ReportLab / xhtml2pdf)
│   ├── urls.py                        # Rutas de visualización analítica y endpoints de descarga PDF
│   ├── templates/dashboard/           # Vistas interactivas (Chart.js con backtesting temporal y toggles visuales)
│   └── tests.py                       # Pruebas del dashboard y generación de reportes
│
├── usuarios/                          # Autenticación, Gobernanza y Control de Acceso (RBAC)
│   ├── models.py                      # Modelos: User, Role (Dueño / Contador / Trabajador / Administrador), Company
│   ├── forms.py                       # Formularios de autenticación y registro con verificación de casillas
│   ├── views.py                       # Sincronización de sesiones, login, registro y redirección inteligente
│   └── mixins.py                      # Mixins de autorización para protección de vistas según rol
│
├── Balances_de_prueba/                # Balances financieros reales (.xlsx) para ensayos y demostraciones
│   ├── COAGRA S.A/                    # Ejercicios contables 2022 a 2026
│   ├── COMERCIAL K SPA/               # Ejercicios contables 2022 a 2026
│   ├── FRUTICOLA VICONTO S.A/         # Ejercicios contables 2022 a 2026
│   └── UNION EL GOLF S.A/             # Ejercicios contables 2022 a 2026
│
├── templates/                         # Plantillas HTML maestras (Bootstrap 5.3 + FontAwesome)
│   ├── base.html                      # Layout principal con navegación lateral responsiva
│   ├── moduloETL/                     # Vistas de carga de balance, ratios e historial
│   ├── moduloTransaccional/           # Vistas de punto de venta (POS) y arqueo de caja
│   └── dashboard/                     # Vistas de control analítico y reportes ejecutivos
│
├── docs/                              # Documentación Técnica, Metodológica y Legal Formal
│   ├── transformacion_ifrs_etl(Tecnico).md # Especificación técnica exhaustiva del pipeline ETL
│   ├── simulador_transformacion_ifrs_etl.html # Simulador visual e interactivo de las etapas del ETL
│   ├── plan_recomendaciones_predictivas.md # Arquitectura de prescripción a 90 días y literatura chilena
│   ├── avisos_legales_y_concursales.md     # Marco legal concursal (Leyes 20.720 y 21.563)
│   ├── roles_y_permisos.md                 # Matriz completa de autorización RBAC por endpoint
│   └── metodologia_medicion_insolvencia.md # Formulación matemática del modelo Altman EMS y ratios
│
├── INSTRUCCIONES_LEVANTAR_PROYECTO.md # Guía paso a paso para levantar el proyecto en entornos locales
├── manage.py                          # CLI de gestión administrativa de Django
├── requirements.txt                   # Dependencias base del entorno virtual
├── requirementsVersionesFijas.txt     # Dependencias con versiones fijadas (pinned) testeadas
└── .env.example                       # Plantilla de variables de entorno (MySQL, Django Secret Key)
```

---

## <a id="módulos-y-características-principales"></a>3. Módulos y Características Principales

* **Control Transaccional de Caja (POS):** Registro diario de ventas desglosado por método de pago (Efectivo, Débito, Crédito, Transferencia), deducción automática de comisiones de adquirencia, retiros controlados de caja chica y arqueo ciego con **justificación obligatoria de descuadres** (NIA 240 / Código de Comercio).
* **Pipeline ETL Financiero Desacoplado:** Ingesta de balances bajo norma CMF/IFRS con detección fonética de cuentas, conversión defensiva de signos contables, comprobación de la ecuación patrimonial y cálculo en memoria de los 7 ratios financieros.
* **Dashboard Predictivo a 90 Días:** Monitoreo visual de la curva de probabilidad de insolvencia ($Q_t \to Q_{t+1}$), selección dinámica de períodos contables, matriz de validación histórica retrospectiva (*backtesting*) y explicabilidad Top 3 mediante valores SHAP.
* **Plan de Acción Preventivo:** Prescripción gerencial estructurada en 3 niveles (*Situación Actual, Acción Recomendada, Paso a Paso Sugerido*) redactada en Lenguaje Ejecutivo Accesible sin tecnicismos abstractos.
* **Reportería Ejecutiva Oficial:** Generación y descarga de informes gerenciales en PDF (`ReportLab` / `xhtml2pdf`) con sellado temporal, firmas de auditoría y deslinde de responsabilidad fiduciaria.

---

## <a id="pipeline-etl-y-normalización-ifrs--cmf"></a>4. Pipeline ETL y Normalización IFRS / CMF

El motor `FinancialETLProcessor` ([`moduloETL/etl_financiero.py`](moduloETL/etl_financiero.py)) opera en memoria sin dependencias de base de datos para garantizar máxima velocidad y portabilidad:

1. **Normalización fonética:** Remoción de tildes, signos de puntuación y unificación a minúsculas canónicas (`normalize_text`).
2. **Parseo numérico defensivo:** Conversión de formatos contables con paréntesis `(monto)` a negativos, supresión de caracteres de moneda (`$`, `CLP`, `UF`) y detección inteligente de puntuación chilena e internacional (`clean_number`).
3. **Detección y exigencia de formato horizontal:** Valida la estructura oficial exigida por la CMF (cuentas contables en columnas y filas temporales por período trimestral).
4. **Regla Fallback de EBIT:** Si el balance omite el Resultado Operacional, se deduce automáticamente mediante:
   $$\text{EBIT} = \text{Ganancia Antes de Impuestos (EBT)} + \text{Costos Financieros}$$
5. **Validaciones Axiomáticas Contables:**
   * Verificación estricta de **Activo Total > 0** (rechazo inmediato si no cumple).
   * Tolerancia de desbalance de la Ecuación Patrimonial $\le 5\%$ ($|\text{Activo} - (\text{Pasivo} + \text{Patrimonio})| / \text{Activo}$).
   * Detección preventiva de **Quiebra Técnica / Insolvencia** ($\text{Patrimonio Neto} \le 0$).
   * Comprobación de coherencia interna ($\text{Activo Circulante} \le \text{Activo Total}$, $\text{Pasivo Circulante} \le \text{Pasivo Total}$).

> [!TIP]
> Puedes utilizar los archivos de la carpeta [`Balances_de_prueba/`](Balances_de_prueba/) para ensayar el pipeline de carga con balances reales de empresas de diversos rubros (agropecuario, comercial, frutícola y deportivo).

---

## <a id="modelo-predictivo-y-fundamento-científico"></a>5. Modelo Predictivo de Machine Learning y Fundamento Científico

El clasificador supervisado se fundamenta en un vector canónico de **7 variables adimensionales** rigurosamente depuradas para el ecosistema PYME, mitigando sesgos de escala e incongruencias de formato:

| ID | Feature / Variable | Categoría | Expresión Contable | Rol en la Detección Temprana |
| :---: | :--- | :--- | :---: | :--- |
| **V1** | **Razón Corriente** | Liquidez Inmediata | $\frac{\text{Activo Circulante}}{\text{Pasivo Circulante}}$ | Capacidad de cobertura de compromisos exigibles a corto plazo. |
| **V2** | **Capital de Trabajo / Activos** | Liquidez Estructural | $\frac{\text{Activo Circulante} - \text{Pasivo Circulante}}{\text{Activo Total}}$ | Magnitud relativa del colchón operativo de maniobra normalizado. |
| **V3** | **Leverage Total** | Endeudamiento | $\frac{\text{Pasivo Total}}{\text{Patrimonio Neto}}$ | Nivel de apalancamiento y compromiso patrimonial frente a acreedores. |
| **V4** | **ROA Operacional** | Rentabilidad | $\frac{\text{EBIT}}{\text{Activo Total}}$ | Eficiencia económica y productividad pura de los activos. |
| **V5** | **Margen Operacional** | Eficiencia de Costos | $\frac{\text{EBIT}}{\text{Ingresos Netos}}$ | Cojín de rentabilidad operativa generado por cada peso facturado. |
| **V6** | **Rotación de Activos** | Eficiencia de Activos | $\frac{\text{Ingresos Netos}}{\text{Activo Total}}$ | Dinamismo comercial y velocidad de rotación del capital invertido. |
| **V7** | **Volatilidad del Flujo** | Volatilidad Operativa | $\frac{\sigma(\text{Flujo Operacional})}{\mu(\text{Ingresos Netos})}$ | Riesgo estocástico de asfixia por iliquidez (Merton / Zurita). |

* **Estrategia de Entrenamiento:** Entrenado sobre estados financieros IFRS de la CMF (2012–2024) etiquetados mediante la zona de riesgo del modelo Altman $Z''_{EM} < 1.10$ o patrimonio neto negativo.
* **Mitigación de Desbalance:** Balanceo de clases mediante *Borderline-SMOTE* filtrado a través de una **matriz de reglas axiomáticas** en Pandas/NumPy para anular registros sintéticos contablemente inconsistentes.
* **Explicabilidad Local (SHAP):** Descomposición de la predicción en las 3 variables con mayor contribución individual marginal (positiva o negativa) al riesgo final.

---

## <a id="dashboard-analítico-y-plan-de-acción-a-90-días"></a>6. Dashboard Analítico y Plan de Acción a 90 Días

El subsistema analítico traduce la probabilidad de insolvencia a la realidad gerencial mediante una **Matriz de Transición Intertemporal ($3 \times 3$)** que evalúa la trayectoria de la empresa entre el período actual ($Q_t$) y el proyectado ($Q_{t+1}$):

* **Semáforos de Riesgo:**
  * 🟢 **Verde (Zona Segura / Solvente):** $\text{Score} \le 35\%$
  * 🟡 **Amarillo (Zona Gris / Alerta Preventiva):** $35\% < \text{Score} \le 70\%$
  * 🔴 **Rojo (Zona Crítica / Alto Riesgo de Quiebra):** $\text{Score} > 70\%$
* **Lenguaje Ejecutivo Accesible (*Business Plain Spanish*):** Diagnósticos financieros traducidos a conceptos comprensibles por cualquier administrador:
  * *"Por cada $1.000 que debe pagar en el corto plazo, dispone de $1.170 en recursos líquidos..."*
  * *"La deuda total con terceros supera en 4.8 veces el patrimonio neto aportado por los dueños..."*
* **Plan de Acción Preventivo:** Emisión de recomendaciones estratégicas y tácticas concretas para renegociación de pasivos, gestión de capital de trabajo y reprogramación de cobranzas.

---

## <a id="control-de-acceso-y-guía-de-uso-por-roles-rbac"></a>7. Control de Acceso y Guía de Uso por Roles (RBAC)

SmartFinanzas implementa un modelo estricto de **Control de Acceso Basado en Roles (RBAC)** con vistas y funciones condicionadas:

| Rol | Usuario | Login (Correo) | Contraseña | Vistas y Funcionalidades Habilitadas |
| :--- | :--- | :--- | :---: | :--- |
| **Dueño** *(Gerencia)* | `TestDueño` | `propietario@test.cl` | `test123` | **Analítica & Control** (Dashboard actual y predictivo), **Módulo ETL** (balances y ratios), **Cierre y Arqueo** de caja diaria e Historial de cierres. |
| **Contador** *(Auditor)* | `TestContador` | `contador@test.cl` | `test123` | **Analítica & Control** (Dashboard actual y predictivo), **Módulo ETL** (carga de estados, ratios e historial) e Historial de cierres en modo auditoría. |
| **Trabajador** *(Cajero)* | `TestTrabajador` | `trabajador@test.cl` | `test123` | **Transaccional:** Registro de Ventas (Punto de Venta / POS), Cierre y Arqueo de caja diaria e Historial de cierres. *(Aislado de balances y tableros gerenciales)*. |
| **Administrador** *(TI / Superuser)* | `TestAdministrador` | `admin@test.cl` | `test123` | Acceso irrestricto a todos los módulos, auditorías, configuraciones y usuarios de la plataforma. |

*(Para más detalles sobre la matriz de rutas protegidas y mixins, consulte [`docs/roles_y_permisos.md`](docs/roles_y_permisos.md)).*

---

## <a id="gobernanza-jurídica-y-certificación-concursal"></a>8. Gobernanza Jurídica y Certificación Concursal

El sistema incorpora un mecanismo de **certificación previa obligatoria** en cumplimiento con el marco legal chileno:
* **Habilitación Dinámica de Botones:** En formularios críticos (Carga de Balances, Cierre de Caja, Registro de Usuarios y Descarga de Informes ML), los botones de envío inician bloqueados (`disabled`).
* **Consentimiento Explícito:** El botón solo se activa cuando el usuario marca de forma voluntaria la casilla de aceptación y certificación legal.
* **Validación en Doble Capa:** Validación dual con JavaScript en frontend y comprobación estricta en el backend de Django (`request.POST.get('terminos_aceptados')`).
* **Alineación con la Ley 20.720 y Ley 21.563:** Información sobre procedimientos de Reorganización Judicial Simplificada para MiPymes, deber de diligencia de administradores y advertencia sobre delitos concursales (insolvencia fraudulenta).

*(Para el análisis jurídico completo, consulte [`docs/avisos_legales_y_concursales.md`](docs/avisos_legales_y_concursales.md)).*

---

## <a id="instalación-y-despliegue-local"></a>9. Instalación y Despliegue Local

Para instrucciones detalladas paso a paso, consulta el documento [`INSTRUCCIONES_LEVANTAR_PROYECTO.md`](INSTRUCCIONES_LEVANTAR_PROYECTO.md).

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/SmartFinanzas.git
cd SmartFinanzas
```

### 2. Crear y activar el entorno virtual
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (CMD):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```
* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirementsVersionesFijas.txt
```
*(Alternativamente puedes usar `pip install -r requirements.txt`).*

### 4. Configurar variables de entorno (`.env`)
Inicia el servicio MySQL/MariaDB (por ejemplo en XAMPP) y crea la base de datos:
```sql
CREATE DATABASE IF NOT EXISTS smartfinanzas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Crea el archivo `.env` en la raíz del proyecto basándote en `.env.example`:
```env
DEBUG=True
SECRET_KEY=django-insecure.......
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartfinanzas o nombre elegido
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Aplicar migraciones
```bash
python manage.py migrate
```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```
Accede a la plataforma en tu navegador web en: **`http://127.0.0.1:8000/`**

---

## <a id="aseguramiento-de-calidad-y-pruebas"></a>10. Aseguramiento de Calidad y Pruebas

* **Suite de Pruebas Unitarias e Integración en Django:**
  ```bash
  # Ejecutar todas las pruebas del monolito modular
  python manage.py test

  # Ejecutar pruebas específicas por módulo
  python manage.py test moduloETL
  python manage.py test capaAnalitica
  python manage.py test dashboard
  ```
* **Pruebas de Carga y Rendimiento:** Verificación de tiempos de respuesta menores a 3 segundos bajo concurrencia simulada con **Apache JMeter**.
* **Auditoría de Seguridad Web:** Protección nativa de Django contra vulnerabilidades críticas del **OWASP Top 10** (Inyección SQL mediante ORM parametrizado, Cross-Site Scripting con escape automático de templates, tokens CSRF obligatorios y cookies de sesión seguras).

---

## <a id="cumplimiento-normativo-y-seguridad"></a>11. Cumplimiento Normativo y Seguridad

* **Protección de Datos Personales:** Diseñado bajo los principios de la **Ley 19.628** sobre Protección de la Vida Privada y adecuado a los estándares de gobernanza y trazabilidad exigidos por la **Ley 21.719**.
* **Estándar de Calidad ISO/IEC 25010:** Cumplimiento riguroso de las dimensiones de **Seguridad**, **Usabilidad**, **Mantenibilidad** y **Fiabilidad** de software.
* **Código de Comercio y NIA 240:** Registro inmutable de transacciones, foliación y justificación obligatoria de diferencias de arqueo en el cierre diario de caja.

---

## <a id="documentación-técnica-y-legal-de-respaldo"></a>12. Documentación Técnica y Legal de Respaldo

En la carpeta [`docs/`](docs/) se encuentra disponible el conjunto de documentación formal del sistema:

1. [`docs/transformacion_ifrs_etl(Tecnico).md`](docs/transformacion_ifrs_etl(Tecnico).md): Especificación técnica del pipeline ETL, normalización canónica, validaciones contables y ratios.
2. [`docs/simulador_transformacion_ifrs_etl.html`](docs/simulador_transformacion_ifrs_etl.html): Simulador interactivo en HTML/JS para visualizar las 6 etapas del procesamiento ETL.
3. [`docs/plan_recomendaciones_predictivas.md`](docs/plan_recomendaciones_predictivas.md): Diseño del Plan de Acción a 90 Días, matriz de transición intertemporal y fundamentación empírica en literatura chilena.
4. [`docs/avisos_legales_y_concursales.md`](docs/avisos_legales_y_concursales.md): Análisis jurídico sobre responsabilidad civil/penal, deberes de administración y procedimientos de la Ley 20.720 y Ley 21.563.
5. [`docs/roles_y_permisos.md`](docs/roles_y_permisos.md): Matriz de autorización RBAC, endpoints y control de acceso por rol.
6. [`docs/metodologia_medicion_insolvencia.md`](docs/metodologia_medicion_insolvencia.md): Fundamento matemático del modelo Altman EMS y justificación de variables financieras.

---

## <a id="autores-y-agradecimientos"></a>13. Autores y Agradecimientos

* **Arturo Quiroga Tello** – Gestión de Proyecto, Desarrollo Fullstack, Ingeniería de Datos & Machine Learning, Testing & QA.
* **Carlos Covarrubias Astudillo** – Docente Guía y Asesoría Metodológica.
* **Juan Pablo Yáñez Riquelme** – Docente Consultor y Asesor Técnico en Machine Learning.
* **Alexis Vázquez & Natalia Pezoa** – Representantes de *Nstock Importaciones* (Validación Operativa y Pruebas de Campo).
* **INACAP Sede La Serena** – Área de Tecnologías de Información y Ciberseguridad.

---
*SmartFinanzas – Innovación analítica y tecnológica aplicada a la preservación de la solvencia empresarial.*
