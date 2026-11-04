"""
URL configuration for SmartFinanzas project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('principal/', TemplateView.as_view(template_name='Principal.html'), name='principal_preview'),
    path('Principal.html', TemplateView.as_view(template_name='Principal.html'), name='principal_html'),
    path('base/', TemplateView.as_view(template_name='Principal.html'), name='base_preview'),
    path('transaccional/', include('moduloTransaccional.urls')),
    path('', include('AppWeb.urls')),
]
