import os, sys
sys.path.insert(0, os.path.abspath('.'))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartFinanzas.settings')
django.setup()

from usuarios.models import Company, Role, User

c = Company.objects.filter(business_name__icontains='COAGRA').first()
print('Company:', c)
for u in User.objects.filter(company=c):
    print(f'User: {u.username}, Role: {u.role.name if u.role else None}')
