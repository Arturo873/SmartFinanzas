from django.urls import path
from .views import VentaCreateView, CierreCajaCreateView, HistorialCierresListView

app_name = 'moduloTransaccional'

urlpatterns = [
    path('ventas/nueva/', VentaCreateView.as_view(), name='venta_crear'),
    path('cierre/nuevo/', CierreCajaCreateView.as_view(), name='cierre_caja'),
    path('cierres/', HistorialCierresListView.as_view(), name='historial_cierres'),
]

