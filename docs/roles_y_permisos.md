# Roles y Permisos (RBAC) en SmartFinanzas

Documento de referencia sobre el control de acceso basado en roles (RBAC) implementado en el proyecto.

---

## 1. Roles Definidos

Los roles se almacenan en el modelo `Role` (`usuarios/models.py`, tabla `role`) y se asignan a cada usuario mediante `User.role`. Si la tabla `role` está vacía al abrir el formulario de registro, `RegistroForm` (`usuarios/forms.py`) crea automáticamente los cuatro roles base:

| Rol | Descripción | Ruta inicial tras iniciar sesión |
| :--- | :--- | :--- |
| **`Dueño`** | Gerencia, visualización de dashboard y arqueos de caja | `/dashboard/` (`dashboard:dashboard`) |
| **`Contador`** | Carga de planillas ETL, predicciones y revisión contable | `/dashboard/` (`dashboard:dashboard`) |
| **`Trabajador`** | Registro de ventas operativas | `/transaccional/ventas/nueva/` (`moduloTransaccional:venta_crear`) |
| **`Administrador`** | Gestión técnica y permisos (acceso en todos los módulos) | `/dashboard/` (`dashboard:dashboard`) |

> **Nota:** Los superusuarios de Django (`is_superuser=True`) tienen acceso habilitado en todos los mixins de control de acceso.

---

## 2. Sincronización de Sesión y Resolución del Rol

Al iniciar sesión o completar el registro, `sincronizar_sesion()` (`usuarios/views.py`):

1. Guarda el rol en la sesión HTTP (`request.session['usuario_rol']`).
2. Vincula al usuario de negocio (`usuarios.models.User`) con `django.contrib.auth.models.User`.
3. Crea o actualiza `AppWeb.models.UserProfile` (`user.profile.role`) con el nombre del rol asignado.
4. Determina la redirección inicial mediante `redireccionar_segun_rol()`:
   - `Trabajador` → `moduloTransaccional:venta_crear`
   - `Dueño`, `Contador`, `Administrador` u otros → `dashboard:dashboard`

Los mixins de autorización consultan el rol en orden de respaldo (`user.profile.role`, `usuarios.models.User.role` y, en el caso del Dashboard, `request.session['usuario_rol']`).

---

## 3. Matriz de Permisos por Módulo y Vista

| Módulo | Vista / Funcionalidad | Ruta URL | `Dueño` | `Contador` | `Trabajador` | `Administrador` | Mixin / Validación |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Dashboard** | Información Actual (`DashboardView`) | `/dashboard/` | Sí | Sí | No | Sí | `DashboardRolMixin` (`dashboard/views.py`) |
| **Dashboard** | Información Predictiva (`DashboardPredictivoView`) | `/dashboard/predictivo/` | Sí | Sí | No | Sí | `DashboardRolMixin` (`dashboard/views.py`) |
| **Dashboard** | Ejecutar Predicción ML (`EjecutarPrediccionDashboardView`) | `/dashboard/ejecutar-prediccion/` | Sí | Sí | No | Sí | `DashboardRolMixin` (`dashboard/views.py`) |
| **Dashboard** | Exportar Informe PDF Actual (`GenerarPDFView`) | `/dashboard/exportar-pdf/` | Sí | Sí | No | Sí | `DashboardRolMixin` (`dashboard/views.py`) |
| **Dashboard** | Exportar Informe PDF Predictivo (`GenerarPDFPredictivoView`) | `/dashboard/exportar-pdf-predictivo/` | Sí | Sí | No | Sí | `DashboardRolMixin` (`dashboard/views.py`) |
| **Módulo ETL** | Carga de Estados Financieros (`CargaArchivoView`) | `/etl/carga/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloETL/views.py`) |
| **Módulo ETL** | Ratios Financieros (`RatiosFinancierosListView`) | `/etl/ratios/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloETL/views.py`) |
| **Módulo ETL** | Ejecutar Análisis ML (`EjecutarAnalisisView`) | `/etl/ejecutar-analisis/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloETL/views.py`) |
| **Módulo ETL** | Historial de Cargas (`HistorialCargasListView`) | `/etl/historial/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloETL/views.py`) |
| **Módulo ETL** | Limpiar Datos (`LimpiarDatosView`) | `/etl/limpiar/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloETL/views.py`) |
| **Módulo ETL** | Descargar Plantilla IFRS (`DescargarPlantillaView`) | `/etl/plantilla/descargar/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloETL/views.py`) |
| **Transaccional** | Registro de Ventas (`VentaCreateView`) | `/transaccional/ventas/nueva/` | No | No | Sí | Sí | `RolRequeridoMixin` (`moduloTransaccional/views.py`) |
| **Transaccional** | Cierre y Arqueo de Caja (`CierreCajaCreateView`) | `/transaccional/cierre/nuevo/` | Sí | No | No | Sí | `RolRequeridoMixin` (`moduloTransaccional/views.py`) |
| **Transaccional** | Historial de Cierres (`HistorialCierresListView`) | `/transaccional/cierres/` | Sí | Sí | No | Sí | `RolRequeridoMixin` (`moduloTransaccional/views.py`) |

---

## 4. Comportamiento ante Acceso No Autorizado

- **Dashboard (`DashboardRolMixin.handle_no_permission`):**
  - Si el usuario autenticado es `Trabajador`, muestra un mensaje informativo y redirige a `moduloTransaccional:venta_crear`.
  - Si es otro rol no autorizado, muestra un mensaje de error y redirige a `moduloTransaccional:venta_crear`.
- **Módulo ETL (`RolRequeridoMixin`):**
  - Hereda el comportamiento estándar de `LoginRequiredMixin` + `UserPassesTestMixin` (devuelve HTTP `403 Forbidden` si está autenticado sin rol permitido, o redirige a `usuarios:login` si no está autenticado).
- **Módulo Transaccional (`RolRequeridoMixin.handle_no_permission`):**
  - Si está autenticado sin el rol requerido, muestra un mensaje de error indicando los roles permitidos y redirige a `dashboard:dashboard`.
  - Si un `Trabajador` intenta abrir *Cierre de Caja* o *Historial de Cierres*, `dashboard:dashboard` vuelve a redirigirlo a `moduloTransaccional:venta_crear`.

---

## 5. Interfaz y Consideraciones para Demo / Pruebas

1. **Insignia visible en la barra superior:** `templates/Principal.html` muestra el nombre del rol activo (`{{ user.profile.role }}`) en la barra superior y en el encabezado del menú lateral.
2. **Menú lateral (sidebar):** Todos los enlaces de navegación (`Dashboard`, `Módulo ETL` y `Transaccional`) se renderizan para usuarios autenticados; la restricción se aplica en el servidor al intentar acceder a cada vista.
   - Excepción en plantilla: `templates/moduloTransaccional/cierrecaja_list.html` oculta el botón de nuevo cierre cuando el usuario no es `Dueño` ni superusuario.
3. **Registro abierto para pruebas:** `templates/usuarios/registro.html` permite seleccionar libremente cualquiera de los cuatro roles al crear una cuenta nueva.
4. **Módulo legacy (`AppWeb`):** Bajo el prefijo `/app/`, `AppWeb/decorators.py` (`@rol_requerido`) y `AppWeb/views.py` conservan validaciones heredadas para `Dueño` y `Contador`.
5. **Archivos relacionados:**
   - `usuarios/models.py`, `usuarios/forms.py`, `usuarios/views.py`, `usuarios/admin.py`
   - `dashboard/views.py`, `moduloETL/views.py`, `moduloTransaccional/views.py`
   - `dashboard/tests.py`, `moduloETL/tests.py`, `moduloTransaccional/tests.py`
