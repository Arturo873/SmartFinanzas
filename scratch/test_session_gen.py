import os, sys
sys.path.insert(0, os.path.abspath('.'))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartFinanzas.settings')
django.setup()

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User as AuthUser
from usuarios.models import User

for username in ['dueno_coagra', 'contador_coagra', 'trabajador_coagra']:
    u_db = User.objects.get(username=username)
    auth_u = AuthUser.objects.get(username=username)
    s = SessionStore()
    s['usuario_id'] = u_db.id
    s['usuario_nombre'] = u_db.username
    s['usuario_rol'] = u_db.role.name
    s['_auth_user_id'] = str(auth_u.id)
    s['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
    s['_auth_user_hash'] = auth_u.get_session_auth_hash()
    s.save()
    print(f"User: {username} -> sessionid={s.session_key}")
