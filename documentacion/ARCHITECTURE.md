# 🏗️ Arquitectura del Proyecto SmartFinanzas

Documentación de la estructura, componentes y organización del proyecto SmartFinanzas.

## 📂 Estructura General del Proyecto

```
SmartFinanzas/
├── manage.py                          # Script de gestión de Django
├── db.sqlite3                         # Base de datos SQLite
├── requirements.txt                   # Dependencias del proyecto (opcional)
│
├── SmartFinanzas/                     # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py                    # Configuración de Django
│   ├── urls.py                        # Rutas principales
│   ├── asgi.py                        # Configuración ASGI (producción)
│   └── wsgi.py                        # Configuración WSGI (producción)
│
├── AppWeb/                            # Aplicación principal
│   ├── __init__.py
│   ├── admin.py                       # Registro de modelos en admin
│   ├── apps.py                        # Configuración de la app
│   ├── models.py                      # Modelos de base de datos
│   ├── views.py                       # Lógica de negocio (vistas)
│   ├── urls.py                        # Rutas de la app
│   ├── tests.py                       # Tests unitarios
│   ├── migrations/                    # Control de versiones de BD
│   │   └── __init__.py
│   └── templates/
│       └── AppWeb/
│           ├── base.html              # Template padre
│           └── index.html             # Página de inicio
│
├── templates/                         # Templates globales (compartidos)
│   └── (templates globales aquí)
│
└── docs/                              # Documentación
    ├── SETUP_WINDOWS.md               # Guía de instalación (Windows)
    ├── SETUP_LINUX.md                 # Guía de instalación (Linux)
    └── ARCHITECTURE.md                # Este archivo
```

## 🔄 Flujo de Datos

```
Usuario (Navegador)
    ↓
URL Request (http://127.0.0.1:8000/)
    ↓
SmartFinanzas/urls.py (Enrutador principal)
    ↓
AppWeb/urls.py (Rutas de la app)
    ↓
AppWeb/views.py (Vista - Lógica de negocio)
    ↓
AppWeb/models.py (Modelos - Interacción con BD)
    ↓
db.sqlite3 (Base de datos)
    ↓
AppWeb/templates/ (Template HTML)
    ↓
Navegador (Respuesta HTML renderizada)
```

## 📋 Componentes Principales

### 1. **SmartFinanzas/** - Configuración Central

#### `settings.py`
Configuración global del proyecto:
- `INSTALLED_APPS` - Apps instaladas (Django + AppWeb)
- `TEMPLATES` - Configuración de templates
- `DATABASES` - Conexión a base de datos
- `MIDDLEWARE` - Procesadores de solicitudes
- `SECRET_KEY` - Clave secreta (cambiar en producción)

#### `urls.py`
Enrutador principal que distribuye las peticiones:
```python
urlpatterns = [
    path('admin/', admin.site.urls),        # Panel de administración
    path('', include('AppWeb.urls')),       # Rutas de AppWeb
]
```

### 2. **AppWeb/** - Aplicación Principal

#### `models.py`
Definición de entidades/tablas de base de datos:
- Aquí irán modelos como: Usuario, Transacción, Categoría, etc.
- Cada modelo = tabla en la BD

#### `views.py`
Lógica de negocio:
```python
def home(request):
    # Obtener datos
    # Procesar lógica
    # Renderizar template
    return render(request, 'AppWeb/index.html', context)
```

#### `urls.py`
Rutas específicas de la app:
```python
urlpatterns = [
    path('', views.home, name='home'),      # Ruta raíz
    # Agregar más rutas aquí
]
```

#### `admin.py`
Registro de modelos en el panel de administración Django:
```python
from django.contrib import admin
from .models import TuModelo

admin.site.register(TuModelo)
```

#### `migrations/`
Historial de cambios en la estructura de la base de datos:
- Se generan automáticamente con `python manage.py makemigrations`
- Se aplican con `python manage.py migrate`

### 3. **templates/** - Interfaz de Usuario

#### Estructura de Templates
```
templates/
├── AppWeb/
│   ├── base.html          # Template padre (herencia)
│   ├── index.html         # Página de inicio
│   ├── profile.html       # (futuro)
│   ├── dashboard.html     # (futuro)
│   └── ...
└── (otros templates globales)
```

#### Sistema de Herencia de Templates
```django
<!-- base.html - Template padre -->
<!DOCTYPE html>
<html>
  <body>
    <nav>{% block navbar %}{% endblock %}</nav>
    <main>{% block content %}{% endblock %}</main>
  </body>
</html>

<!-- index.html - Hereda de base.html -->
{% extends "AppWeb/base.html" %}
{% block content %}
  <h1>Contenido específico</h1>
{% endblock %}
```

## 🗄️ Base de Datos

### SQLite3 (Desarrollo)
- Archivo: `db.sqlite3`
- Ideal para desarrollo local
- No recomendado para producción

### Migraciones
```bash
# Crear migraciones después de cambios en modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations
```

### Flujo de Cambios en BD
```
Editar models.py
    ↓
python manage.py makemigrations (crea archivo en migrations/)
    ↓
python manage.py migrate (aplica cambios a db.sqlite3)
```

## 🔐 Administración

### Panel de Admin Django
- **URL**: http://127.0.0.1:8000/admin/
- **Credenciales**: Creadas con `python manage.py createsuperuser`
- **Uso**: Gestión CRUD de modelos registrados

```python
# AppWeb/admin.py
from django.contrib import admin
from .models import Transaccion, Categoria

admin.site.register(Transaccion)
admin.site.register(Categoria)
```

## 📊 Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Backend | Django | 6.0.5 |
| Base de Datos | SQLite3 | Incluido |
| Frontend | HTML5 + Bootstrap | 5.3 |
| Lenguaje | Python | 3.8+ |

## 🚀 Flujo de Desarrollo

### 1. Crear un Modelo
```python
# AppWeb/models.py
class Transaccion(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
```

### 2. Migrar Cambios
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Registrar en Admin (opcional)
```python
# AppWeb/admin.py
admin.site.register(Transaccion)
```

### 4. Crear Vista
```python
# AppWeb/views.py
def transacciones(request):
    transacciones = Transaccion.objects.all()
    return render(request, 'AppWeb/transacciones.html', {'transacciones': transacciones})
```

### 5. Agregar Ruta
```python
# AppWeb/urls.py
path('transacciones/', views.transacciones, name='transacciones'),
```

### 6. Crear Template
```django
<!-- AppWeb/templates/AppWeb/transacciones.html -->
{% extends "AppWeb/base.html" %}
{% block content %}
  {% for t in transacciones %}
    <p>{{ t.monto }} - {{ t.fecha }}</p>
  {% endfor %}
{% endblock %}
```

## 📦 Estructura Recomendada para Futuras Apps

Si necesitas agregar más aplicaciones:

```bash
python manage.py startapp NuevaApp
```

Estructura resultante:
```
NuevaApp/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── migrations/
└── templates/NuevaApp/
```

**Agregar a `INSTALLED_APPS` en settings.py:**
```python
INSTALLED_APPS = [
    # ...
    'AppWeb',
    'NuevaApp',  # Nueva app
]
```

## 🔒 Configuración de Producción

Para pasar a producción, cambiar en `settings.py`:

```python
DEBUG = False  # Desactivar modo debug
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']
SECRET_KEY = 'generar-nueva-clave-secreta-aleatoria'

# Usar PostgreSQL o MySQL en lugar de SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartfinanzas_db',
        'USER': 'usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📝 Notas Importantes

- **Siempre activar el entorno virtual** antes de trabajar
- **Nunca commitear** la carpeta `venv/` ni `db.sqlite3` en producción
- **Cambiar SECRET_KEY** en producción
- **Usar variables de entorno** para configuración sensible
- **Crear archivo `.gitignore`** para no subir archivos innecesarios

## 🎯 Próximos Pasos

1. Definir modelos en `AppWeb/models.py`
2. Crear migraciones y aplicarlas
3. Registrar modelos en admin
4. Crear vistas (views)
5. Crear templates correspondientes
6. Agregar rutas (URLs)
7. Implementar tests en `tests.py`

---

**Última actualización**: 2026-06-10
