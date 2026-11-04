from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_direct'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
]

