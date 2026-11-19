"""
Context Processor global de seguridad y control de acceso por capacidades (RBAC / Capability-Based).
Desacopla completamente las plantillas HTML de nombres literales de roles ('Dueño', 'Contador', etc.).
Las plantillas solo evalúan variables booleanas de capacidades:
    - permisos.ver_analitica
    - permisos.ver_etl
    - permisos.operar_ventas
    - permisos.cerrar_caja
    - permisos.ver_historial_cierres
    - permisos.es_operativo_caja
"""

def permisos_usuario(request):
    """
    Inyecta el diccionario 'permisos' en el contexto de todas las plantillas Django.
    """
    permisos_default = {
        'ver_analitica': False,
        'ver_etl': False,
        'operar_ventas': False,
        'cerrar_caja': False,
        'ver_historial_cierres': False,
        'es_operativo_caja': False,
    }

    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'permisos': permisos_default}

    is_super = getattr(user, 'is_superuser', False)

    # 1. Obtener rol desde sesión HTTP (estrategia de alta velocidad)
    rol = None
    if hasattr(request, 'session'):
        rol = request.session.get('usuario_rol')

    # 2. Respaldo: perfil OneToOne (AppWeb)
    if not rol and hasattr(user, 'profile') and user.profile:
        rol = getattr(user.profile, 'role', None)

    # 3. Respaldo: modelo User de usuarios
    if not rol:
        try:
            from usuarios.models import User as UserModel
            usuario_db = UserModel.objects.select_related('role').filter(username=user.username).first()
            if usuario_db and usuario_db.role:
                rol = usuario_db.role.name
        except Exception:
            rol = None

    # Normalización para tolerancia a mayúsculas/minúsculas y acentos
    rol_str = str(rol).strip().lower() if rol else ''

    es_trabajador = (rol_str == 'trabajador')
    es_contador = (rol_str == 'contador')
    es_dueno = (rol_str in ['dueño', 'dueno'])
    es_admin = (rol_str in ['administrador', 'admin'] or is_super)

    permisos = {
        'ver_analitica': bool(es_dueno or es_contador or es_admin),
        'ver_etl': bool(es_contador or es_dueno or es_admin),
        'operar_ventas': bool(es_trabajador or es_admin),
        'cerrar_caja': bool(es_trabajador or es_dueno or es_admin),
        'ver_historial_cierres': bool(es_trabajador or es_dueno or es_contador or es_admin),
        'es_operativo_caja': bool(es_trabajador and not es_admin),
    }

    # Si la sesión está disponible, sincronizar también la clave 'permisos'
    if hasattr(request, 'session') and 'permisos' not in request.session:
        try:
            request.session['permisos'] = permisos
        except Exception:
            pass

    return {'permisos': permisos}
