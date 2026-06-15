# 🪟 Configuración de SmartFinanzas en Windows

Guía paso a paso para instalar y ejecutar SmartFinanzas en Windows desde cero.

## Requisitos previos

- Windows 10/11
- Acceso a terminal (CMD, PowerShell o Git Bash)
- Conexión a internet

## 1. Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Ejecuta el instalador
3. **Importante**: Marca la opción ✓ "Add Python to PATH"
4. Completa la instalación

### Verificar instalación:
```cmd
python --version
pip --version
```

## 2. Clonar o abrir el repositorio

Abre PowerShell/CMD en la carpeta del proyecto:
```cmd
cd C:\ruta\al\proyecto\SmartFinanzas
```

## 3. Crear entorno virtual

```cmd
python -m venv venv
```

## 4. Activar entorno virtual

### Con PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

**Si tienes error de permisos**, ejecuta en PowerShell como administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Con CMD:
```cmd
venv\Scripts\activate.bat
```

### Con Git Bash:
```bash
source venv/Scripts/activate
```

## 5. Instalar dependencias

```cmd
pip install django
pip install pandas
pip install pandas openpyxl
```

O si tienes un archivo `requirements.txt`:
```cmd
pip install -r requirements.txt
```

## 6. Realizar migraciones

```cmd
python manage.py migrate
```

## 7. Crear superusuario (administrador)(OPCIONAL)

```cmd
python manage.py createsuperuser
```

Ingresa:
- **Nombre de usuario**: admin
- **Email**: tu@email.com
- **Contraseña**: (ingresa una contraseña segura)

## 8. Ejecutar servidor de desarrollo

```cmd
python manage.py runserver
```

## 9. Acceder a la aplicación

Abre tu navegador y ve a:
- **Aplicación**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Troubleshooting

### Error: `python: command not found`
- Reinstala Python y marca "Add Python to PATH"
- Reinicia la terminal después de instalar

### Error: `No module named 'django'`
- Verifica que el entorno virtual está activado (debe haber `(venv)` en el prompt)
- Ejecuta: `pip install django`

### Error al activar entorno virtual
- Intenta con: `venv\Scripts\activate.bat` (CMD)
- O: `.\venv\Scripts\Activate.ps1` (PowerShell como administrador)

### Puerto 8000 ya está en uso
```cmd
python manage.py runserver 8001
```

## Comandos útiles

```cmd
# Desactivar entorno virtual
deactivate

# Ver paquetes instalados
pip list

# Crear migraciones después de cambios en modelos
python manage.py makemigrations

# Ver migraciones pendientes
python manage.py showmigrations

# Ejecutar servidor en otro puerto
python manage.py runserver 0.0.0.0:8001
```

## ¿Ya está todo listo?

Si viste mensajes sin errores, ¡estás listo! 🎉

Accede a http://127.0.0.1:8000/ para ver la aplicación.
