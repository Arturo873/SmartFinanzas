from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('', views.home, name='home'),
    path('carga-datos/', views.carga_datos, name='carga_datos'),
    path('capm/', views.calculo_capm, name='capm'),
    path('prediccion/', views.ejecutar_prediccion, name='prediccion'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('limpiar/', views.limpiar_datos, name='limpiar_datos'),
]
