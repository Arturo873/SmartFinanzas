"""
Rutas URL para el Módulo ETL de SmartFinanzas.
"""

from django.urls import path
from . import views

app_name = 'moduloETL'

urlpatterns = [
    path('carga/', views.CargaArchivoView.as_view(), name='carga_datos'),
    path('ratios/', views.RatiosFinancierosListView.as_view(), name='ratios_financieros'),
    path('historial/', views.HistorialCargasListView.as_view(), name='historial_cargas'),
    path('limpiar/', views.LimpiarDatosView.as_view(), name='limpiar_datos'),
    path('plantilla/descargar/', views.DescargarPlantillaView.as_view(), name='descargar_plantilla'),
]

