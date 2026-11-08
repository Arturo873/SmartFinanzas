"""
Rutas URL para el Módulo ETL de SmartFinanzas.
"""

from django.urls import path
from . import views

app_name = 'moduloETL'

urlpatterns = [
    path('carga/', views.CargaArchivoView.as_view(), name='carga_datos'),
    path('carga-nueva/', views.CargaArchivoNuevoView.as_view(), name='carga_datos_nuevo'),
    path('ratios/', views.RatiosFinancierosListView.as_view(), name='ratios_financieros'),
    path('historial/', views.HistorialCargasListView.as_view(), name='historial_cargas'),
    path('limpiar/', views.LimpiarDatosView.as_view(), name='limpiar_datos'),
    path('plantilla/descargar/', views.DescargarPlantillaView.as_view(), name='descargar_plantilla'),
    path('ejecutar-analisis/', views.EjecutarAnalisisView.as_view(), name='ejecutar_analisis'),
]

