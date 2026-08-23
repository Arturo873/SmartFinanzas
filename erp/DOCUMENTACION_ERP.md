# Módulo ERP - Nstock Importaciones

Este módulo integra las funcionalidades de Catálogo, Inventario y Proveedores dentro del proyecto **SmartFinanzas**. Se implementó usando un enfoque de "aplicación paraguas", en el cual la carpeta `erp` agrupa y gestiona estas sub-aplicaciones para mantener el código ordenado.

## 🛠️ Estructura del Módulo

- **`erp.catalogo`**: Gestión de categorías y productos.
- **`erp.inventario`**: Administración de bodegas y movimientos de stock (entradas, salidas y traslados).
- **`erp.proveedores`**: Registro de países, divisiones administrativas y directorio de proveedores.
- **`erp/templates/erp/`**: Contiene todos los archivos HTML del módulo, unificados bajo un tema visual **amarillo/dorado**.
- **`erp/static/erp/`**: Archivos CSS, JavaScript e imágenes propios del sistema.
- **`erp/urls.py`**: Enrutador centralizado que expone todas las URLs usando el prefijo interno `erp_`.
- **`erp/routers.py`**: Configuración de enrutamiento de base de datos para separar los datos del ERP de los datos de la aplicación original.

## ⚙️ Arquitectura de Base de Datos (Database Routing)

Para evitar mezclar los datos financieros antiguos con los del nuevo ERP, el sistema soporta **múltiples bases de datos**.

1. **`default` (SQLite)**: Almacena los usuarios, permisos y toda la información de `AppWeb`.
2. **`erp_db` (MySQL)**: Almacena exclusivamente las tablas de `catalogo`, `inventario` y `proveedores`. 

Esta separación se gestiona automáticamente gracias a la clase `ERPRouter` ubicada en `erp/routers.py`.

### Comandos de Migración

Dado que existen dos bases de datos, los comandos de migración se deben ejecutar de la siguiente manera:

* **Migrar AppWeb (SQLite):**
  ```bash
  python manage.py migrate
  ```
* **Migrar ERP (MySQL):**
  ```bash
  python manage.py migrate --database=erp_db
  ```

## 🔒 Autenticación y Usuarios

En esta versión inicial del módulo, **se ha removido toda dependencia a sistemas de inicio de sesión o gestión de roles**. 
Cualquier usuario que ingrese a la ruta `/erp/` o `/erp/mantenedores/` tiene acceso temporal de administrador a todas las vistas y acciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre los productos, el inventario y los proveedores.

## 🎨 Tema Visual

Se migró la estética corporativa original (que utilizaba colores rojos oscuros) hacia un esquema amarillo utilizando clases de Bootstrap (`btn-warning`, `alert-warning`, `text-warning`) y reglas CSS manuales configuradas para fondos claros como `#fffdf5` y elementos primarios en `#ffc107`. Todo el etiquetado y contenido referenciado fue reemplazado por **Nstock Importaciones**.
