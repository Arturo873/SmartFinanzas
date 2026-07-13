from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def rol_requerido(*roles_permitidos):
    def decorador(vista):
        @login_required(login_url='login')
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            perfil = getattr(request.user, 'perfil', None)
            if not perfil or perfil.rol not in roles_permitidos:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('home')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador
