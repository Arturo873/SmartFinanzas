from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import TemplateView

from .models import Usuario
from .forms import LoginForm, RegistroForm
from AppWeb.models import PerfilUsuario


def sincronizar_sesion(request, usuario_db):
    """
    Sincroniza la autenticación entre el modelo Usuario
    y el subsistema de sesiones y usuarios de Django (auth.User + PerfilUsuario).
    """
    # 1. Actualizar última sesión
    usuario_db.ultima_sesion = timezone.now()
    usuario_db.save(update_fields=['ultima_sesion'])

    # 2. Guardar datos en la sesión HTTP
    request.session['usuario_id'] = usuario_db.id
    request.session['usuario_nombre'] = usuario_db.username
    request.session['usuario_rol'] = usuario_db.rol.nombre if usuario_db.rol else 'Usuario'

    # 3. Vincular con auth.User para que request.user y los decoradores/mixins funcionen al 100%
    auth_user, _ = User.objects.get_or_create(
        username=usuario_db.username,
        defaults={'email': usuario_db.email or ''}
    )
    if usuario_db.rol:
        PerfilUsuario.objects.update_or_create(
            user=auth_user,
            defaults={'rol': usuario_db.rol.nombre}
        )

    # Iniciar sesión oficial en Django
    auth_login(request, auth_user)


def login_view(request):
    """
    Vista de inicio de sesión que autentica usuarios en el sistema.
    Redirige a 'principal' tras una autenticación exitosa.
    """
    if request.user.is_authenticated:
        return redirect('principal')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        usuario_db = form.cleaned_data['usuario_db']
        sincronizar_sesion(request, usuario_db)
        messages.success(request, f"Bienvenido(a), {usuario_db.username} ({usuario_db.rol.nombre if usuario_db.rol else 'Usuario'}).")
        return redirect('principal')

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
        return redirect('principal')

    form = RegistroForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        usuario_db = form.save()
        sincronizar_sesion(request, usuario_db)
        messages.success(
            request,
            f"¡Cuenta creada con éxito! Has sido registrado como {usuario_db.rol.nombre}."
        )
        return redirect('principal')

    return render(request, 'usuarios/registro.html', {'form': form})
