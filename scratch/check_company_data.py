import os, sys
sys.path.insert(0, os.path.abspath('.'))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartFinanzas.settings')
django.setup()

from usuarios.models import Company
from moduloETL.models import FinancialRatio
from capaAnalitica.models import RiskPrediction
from moduloTransaccional.models import Sale, CashRegisterClosure

for c in Company.objects.all():
    print(f'Company {c.id}: {c.business_name} | Ratios: {FinancialRatio.objects.filter(company=c).count()} | Predictions: {RiskPrediction.objects.filter(company=c).count()} | Sales: {Sale.objects.filter(company=c).count()} | Closures: {CashRegisterClosure.objects.filter(company=c).count()}')
