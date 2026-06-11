from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('carga-datos/', views.carga_datos, name='carga_datos'),
    path('capm/', views.calculo_capm, name='capm'),
    path('prediccion/', views.ejecutar_prediccion, name='prediccion'),
]
