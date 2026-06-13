# 🐧 Configuración de SmartFinanzas en Linux

Guía paso a paso para instalar y ejecutar SmartFinanzas en Linux desde cero.

## Requisitos previos

- Linux (Ubuntu, Debian, Fedora, etc.)
- Acceso a terminal
- Conexión a internet
- Permisos de usuario (sudo cuando sea necesario)

## 1. Actualizar repositorios e instalar Python

### Para Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Para Fedora:
```bash
sudo dnf install python3 python3-pip
```

### Para Arch:
```bash
sudo pacman -S python python-pip
```

### Verificar instalación:
```bash
python3 --version
pip3 --version
```

## 2. Navegar al directorio del proyecto

```bash
cd ~/ruta/al/proyecto/SmartFinanzas
```

O si está en otro lugar:
```bash
cd /ruta/completa/SmartFinanzas
```

## 3. Crear entorno virtual

```bash
python3 -m venv venv
```

## 4. Activar entorno virtual

```bash
source venv/bin/activate
#source mi_entorno/bin/activate
#para desactivar solo poner: deactivate
```

Verás que el prompt cambia a algo como: `(venv) usuario@maquina:~/SmartFinanzas$`

## 5. Instalar dependencias

```bash
pip install --upgrade pip
pip install django
```

O si tienes un archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

## 6. Realizar migraciones

```bash
python manage.py migrate
```

## 7. Crear superusuario (administrador)(OPCIONAL)

```bash
python manage.py createsuperuser
```

Ingresa:
- **Nombre de usuario**: admin
- **Email**: tu@email.com
- **Contraseña**: (ingresa una contraseña segura)

## 8. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

## 9. Acceder a la aplicación

Abre tu navegador y ve a:
- **Aplicación**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Troubleshooting

### Error: `python3: command not found`
```bash
sudo apt install python3
```

### Error: `No module named 'django'`
- Verifica que el entorno virtual está activado (debe haber `(venv)` en el prompt)
- Ejecuta: `pip install django`

### Error: `Permission denied` en venv/bin/activate
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### Puerto 8000 ya está en uso
```bash
python manage.py runserver 8001
```

O para encontrar qué proceso usa el puerto:
```bash
lsof -i :8000
# Luego matar el proceso si es necesario
kill -9 <PID>
```

## Script de automatización (opcional)

Crea un archivo `setup.sh` en la raíz del proyecto:

```bash
#!/bin/bash

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install django
pip install pandas
pip install pandas openpyxl

o ejecutar en el entorno virtual pip install -r requirements.txt

# Realizar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

echo "✅ Configuración completada!"
echo "Ejecuta: source venv/bin/activate"
echo "Luego: python manage.py runserver"
```

Hazlo ejecutable:
```bash
chmod +x setup.sh
./setup.sh
```

## Comandos útiles

```bash
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

# Ejecutar servidor accesible desde otros equipos
python manage.py runserver 0.0.0.0:8000
```

## Ejecutar en segundo plano

Si quieres que el servidor continúe ejecutándose incluso si cierras la terminal:

```bash
nohup python manage.py runserver > server.log 2>&1 &
```

Ver logs:
```bash
tail -f server.log
```

Detener el servidor:
```bash
pkill -f "python manage.py runserver"
```

desactivar entorno virtual:
solo poner deaactivate
## ¿Ya está todo listo?

Si viste mensajes sin errores, ¡estás listo! 🎉

Accede a http://127.0.0.1:8000/ para ver la aplicación.
