from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
from django.views.generic import TemplateView

from .models import User, Company
from .forms import LoginForm, RegistroForm
from AppWeb.models import UserProfile


def sincronizar_sesion(request, usuario_db):
    """
    Sincroniza la autenticación entre el modelo User
    y el subsistema de sesiones y usuarios de Django (auth.User + UserProfile).
    """
    # 1. Actualizar última sesión
    usuario_db.last_login = timezone.now()
    usuario_db.save(update_fields=['last_login'])

    # 2. Guardar datos en la sesión HTTP
    request.session['usuario_id'] = usuario_db.id
    request.session['usuario_nombre'] = usuario_db.username
    request.session['usuario_rol'] = usuario_db.role.name if usuario_db.role else 'Usuario'

    # 3. Vincular con auth.User para que request.user y los decoradores/mixins funcionen al 100%
    auth_user, _ = AuthUser.objects.get_or_create(
        username=usuario_db.username,
        defaults={'email': usuario_db.email or ''}
    )
    if usuario_db.role:
        UserProfile.objects.update_or_create(
            user=auth_user,
            defaults={'role': usuario_db.role.name}
        )

    # Iniciar sesión oficial en Django
    auth_login(request, auth_user)


def redireccionar_segun_rol(usuario_db):
    """
    Determina la URL de destino según el rol del usuario:
    - Trabajador: Punto de Venta Operativo (moduloTransaccional:venta_crear).
    - Dueño / Contador / Administrador / Otros: Panel Gerencial (dashboard:dashboard).
    """
    if usuario_db and usuario_db.role and usuario_db.role.name == 'Trabajador':
        return 'moduloTransaccional:venta_crear'
    return 'dashboard:dashboard'


def login_view(request):
    """
    Vista de inicio de sesión que autentica usuarios en el sistema.
    Redirige a 'dashboard:dashboard' (o POS si Trabajador) tras una autenticación exitosa.
    """
    if request.user.is_authenticated:
        usuario_db = User.objects.select_related('role').filter(username=request.user.username).first()
        return redirect(redireccionar_segun_rol(usuario_db))

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        usuario_db = form.cleaned_data['usuario_db']
        sincronizar_sesion(request, usuario_db)
        messages.success(request, f"Bienvenido(a), {usuario_db.username} ({usuario_db.role.name if usuario_db.role else 'Usuario'}).")
        return redirect(redireccionar_segun_rol(usuario_db))

    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """
    Cierre de sesión que limpia cookies y sesiones activas.
    """
    auth_logout(request)
    request.session.flush()
    messages.success(request, "Has cerrado tu sesión de forma segura.")
    return redirect('usuarios:login')


def registro_view(request):
    """
    Vista de registro de nuevos usuarios en el sistema.
    """
    if request.user.is_authenticated:
        usuario_db = User.objects.select_related('role').filter(username=request.user.username).first()
        return redirect(redireccionar_segun_rol(usuario_db))

    form = RegistroForm(request.POST or None)

    if request.method == 'POST':
        terminos_aceptados = request.POST.get('terminos_aceptados')
        if not terminos_aceptados:
            form.add_error(None, "Debe aceptar los Términos de Servicio, Tratamiento de Datos y Confidencialidad para registrarse.")
        elif form.is_valid():
            usuario_db = form.save()
            sincronizar_sesion(request, usuario_db)
            messages.success(
                request,
                f"¡Cuenta creada con éxito! Has sido registrado como {usuario_db.role.name}."
            )
            return redirect(redireccionar_segun_rol(usuario_db))

    empresas = list(Company.objects.all().order_by('id'))
    return render(request, 'usuarios/registro.html', {
        'form': form,
        'empresas': empresas,
    })
