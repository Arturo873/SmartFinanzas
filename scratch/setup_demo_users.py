import os, sys
sys.path.insert(0, os.path.abspath('.'))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartFinanzas.settings')
django.setup()

from django.contrib.auth.models import User as AuthUser
from usuarios.models import Company, Role, User
from AppWeb.models import UserProfile

c = Company.objects.filter(business_name__icontains='COAGRA').first()
roles = {r.name: r for r in Role.objects.all()}

users_config = [
    ('dueno_coagra', 'Dueño', 'dueno@coagra.cl'),
    ('contador_coagra', 'Contador', 'contador@coagra.cl'),
    ('trabajador_coagra', 'Trabajador', 'trabajador@coagra.cl'),
    ('coagra', 'Administrador', 'admin@coagra.cl'),
]

password_raw = 'SmartFinanzas2026!'

for username, role_name, email in users_config:
    role = roles.get(role_name)
    user_db, created = User.objects.get_or_create(username=username, defaults={'company': c, 'email': email, 'role': role})
    user_db.role = role
    user_db.company = c
    user_db.email = email
    user_db.set_password(password_raw)
    user_db.is_active = True
    user_db.save()

    auth_u, _ = AuthUser.objects.get_or_create(username=username, defaults={'email': email})
    auth_u.set_password(password_raw)
    auth_u.is_active = True
    auth_u.save()

    UserProfile.objects.update_or_create(
        user=auth_u,
        defaults={'role': role_name}
    )
    print(f'Configured {username} as {role_name} (Created: {created})')
