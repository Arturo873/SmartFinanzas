"""
Rutas URL para la app Dashboard (Capa de Presentación Gerencial).
SmartFinanzas.
"""

from django.urls import path
from .views import DashboardView, GenerarPDFView, EjecutarPrediccionDashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('index/', DashboardView.as_view(), name='index'),
    path('exportar-pdf/', GenerarPDFView.as_view(), name='generar_pdf'),
    path('pdf/', GenerarPDFView.as_view(), name='exportar_pdf'),
    path('ejecutar-prediccion/', EjecutarPrediccionDashboardView.as_view(), name='ejecutar_prediccion'),
    path('ejecutar-analisis/', EjecutarPrediccionDashboardView.as_view(), name='ejecutar_analisis'),
]
