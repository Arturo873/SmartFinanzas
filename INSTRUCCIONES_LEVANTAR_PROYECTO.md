# 🚀 Guía Rápida para Levantar el Proyecto SmartFinanzas

Esta guía detalla paso a paso cómo configurar, inicializar y ejecutar la plataforma **SmartFinanzas** en un entorno local (Windows / Linux / macOS).

---

## 📋 1. Requisitos Previos

Asegúrate de contar con las siguientes herramientas instaladas:
* **Python**: Versión 3.11 o superior (probado y compatible con Python 3.14).
* **MySQL / MariaDB**: Motor de base de datos activo en el puerto `3306` (por ejemplo, mediante **XAMPP**, **WampServer** o servicio de MySQL Server).
* **Git**: Para el control de versiones.

---

## 🔑 2. Credenciales de Prueba (Cuentas de Test por Rol)

Para ingresar a la plataforma y validar el **Control de Acceso Basado en Roles (RBAC)** y el renderizado condicional de funciones en el menú, se dispone de las siguientes cuentas preconfiguradas:

> **Contraseña universal para todas las cuentas de prueba:** `test123`

| Rol | Usuario | Correo Electrónico (Login) | Contraseña | Vistas y Funciones Habilitadas |
| :--- | :--- | :--- | :---: | :--- |
| **Dueño** *(Gerencia)* | `TestDueño` | `propietario@test.cl` | `test123` | **Analítica & Control** (Dashboard actual y predictivo), **Módulo ETL** (balances y ratios), **Cierre y Arqueo** de gaveta e Historial de cierres. |
| **Contador** *(Auditor)* | `TestContador` | `contador@test.cl` | `test123` | **Analítica & Control** (Dashboard actual y predictivo), **Módulo ETL** (carga de estados, ratios e historial) e Historial de cierres en modo auditoría. |
| **Trabajador** *(Cajero)* | `TestTrabajador` | `trabajador@test.cl` | `test123` | **Transaccional:** Registro de Ventas (Punto de Venta / POS), Cierre y Arqueo de caja diaria e Historial de cierres. *(Aislado de balances y tableros gerenciales)*. |
| **Administrador** *(TI / Superuser)* | `TestAdministrador` | `admin@test.cl` | `test123` | Acceso total e irrestricto a todos los módulos, reportes y configuraciones del sistema. |

> [!NOTE]
> * **Inicio de Sesión:** El formulario de login valida las credenciales utilizando el **Correo Electrónico** y la **Contraseña**.
> * *(Cuenta de prueba administrativa previa: `tes1@test.cl` / `test1@test.cl` con clave `test123`).*
> * **Balances de prueba:** En la carpeta [`Balances_de_prueba/`](SmartFinanzas/Balances_de_prueba) dispones de estados financieros reales en formato `.xlsx` listos para probar la plataforma (empresas: *COAGRA S.A*, *COMERCIAL K SPA*, *FRUTICOLA VICONTO S.A* y *UNION EL GOLF S.A*).

---

## ⚙️ 3. Pasos de Instalación y Despliegue

### Paso 1: Abrir la terminal en la raíz del proyecto
Ubícate en la carpeta principal del proyecto:
```bash
cd SmartFinanzas
```

---

### Paso 2: Activar el entorno virtual

Si ya cuentas con la carpeta `venv`:
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell restringe la ejecución de scripts, ejecuta primero: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

* **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

> [!NOTE]
> Si no existe el entorno virtual, créalo con:
> `python -m venv venv` y luego actívalo con los comandos anteriores.

---

### Paso 3: Instalar las dependencias de Python

Instala los paquetes necesarios utilizando el archivo de versiones fijas para asegurar compatibilidad total:

```bash
pip install --upgrade pip
pip install -r requirementsVersionesFijas.txt
```

*(Alternativamente, puedes usar `pip install -r requirements.txt`).*

---

### Paso 4: Configurar la Base de Datos y Variables de Entorno (`.env`)

1. **Iniciar el servicio MySQL / MariaDB**:
   * En **XAMPP Control Panel**, presiona **Start** en el módulo **MySQL**.

2. **Crear la base de datos**:
   * Abre phpMyAdmin (`http://localhost/phpmyadmin/`) o tu cliente MySQL y crea la base de datos:
     ```sql
     CREATE DATABASE IF NOT EXISTS smartfinanzas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```
   * *(Opcional)* Si cuentas con el respaldo SQL inicial del proyecto, puedes importar `smartfinanzas.sql` en dicha base de datos.

3. **Verificar el archivo `.env` en la raíz del proyecto**:
   Crea o verifica el archivo `.env` con la siguiente configuración:

   ```env
   # Configuración de Entorno Django
   DEBUG=True
   SECRET_KEY=django-insecure-tx!@obs@8uu=6h(uftth-8%=$7v4_xlu5pvq6(qv)kjj4uscv$

   # Conexión a Base de Datos MySQL / MariaDB
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=smartfinanzas
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

   > [!IMPORTANT]
   > Usa `DB_HOST=127.0.0.1` en lugar de `localhost` en Windows para evitar retrasos por resolución IPv6 (`::1`) en el conector MariaDB/MySQL.

---

### Paso 5: Aplicar migraciones

Ejecuta las migraciones de Django para asegurar que todas las tablas y esquemas estén actualizados:

```bash
python manage.py migrate
```

---

### Paso 6: Iniciar el Servidor de Desarrollo

Ejecuta el servidor con el siguiente comando:

```bash
python manage.py runserver
```

El servidor quedará disponible en:
👉 **`http://127.0.0.1:8000/`**

---

## 🧭 4. Navegación y Uso del Sistema

1. **Pantalla de Inicio de Sesión (`/`)**:
   * Ingresa con el correo `tes1@test.cl` y la contraseña `test123`.
   * Al autenticarte serás redirigido automáticamente al panel principal (`/principal/`).

2. **Módulo ETL (Carga de Balances y Ratios Financieros)**:
   * **Carga de Archivo:** Menú lateral → *Módulo ETL* → *Carga de Datos* (`/etl/carga/`).
     * Permite subir balances contables en `.csv` o `.xlsx`.
     * Los datos se vinculan automáticamente a la empresa de tu usuario.
     * Puedes descargar la plantilla oficial directamente desde el botón **"Descargar Plantilla CSV"** (`/etl/descargar-plantilla/`).
     * **Archivos de prueba disponibles:** En la carpeta [`Balances_de_prueba/` dispones de balances financieros reales en formato Excel (`.xlsx`) correspondientes a ejercicios de los años 2022 a 2026 para diferentes empresas:
       * `COAGRA S.A/`
       * `COMERCIAL K SPA/`
       * `FRUTICOLA VICONTO S.A/`
       * `UNION EL GOLF S.A/`
       *(Puedes seleccionar cualquiera de estos archivos para ensayar el pipeline de carga, normalización CMF e inferencia ML).*
   * **Matriz de Ratios:** Menú lateral → *Ratios Financieros* (`/etl/ratios/`).
     * Muestra las 7 variables predictivas (V1 a V7), Altman $Z''_{EM}$, liquidez y solvencia filtradas estrictamente para tu empresa.
   * **Historial de Cargas:** Menú lateral → *Historial de Cargas* (`/etl/historial/`).

3. **Módulo Transaccional (Caja y Métodos de Pago)**:
   * Accede desde el menú lateral para gestionar ventas, cierres diarios de caja y comisiones de adquirencia (`/transaccional/`).

4. **Capa Analítica y Predicción de Riesgo**:
   * Acceso al motor de Machine Learning que calcula la probabilidad de insolvencia y semáforos de alerta financiera (`/app/`).

---

## 🧪 5. Verificación de Pruebas Unitarias

Para comprobar la integridad del sistema y el aislamiento multi-empresa:

```bash
python manage.py test moduloETL
```

