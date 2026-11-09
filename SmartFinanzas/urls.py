"""
URL configuration for SmartFinanzas project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('principal/', TemplateView.as_view(template_name='Principal.html'), name='principal'),
    path('Principal.html', TemplateView.as_view(template_name='Principal.html'), name='principal_html'),
    path('home/', TemplateView.as_view(template_name='Principal.html'), name='home'),
    path('base/', TemplateView.as_view(template_name='Principal.html'), name='base_preview'),
    path('transaccional/', include('moduloTransaccional.urls')),
    path('etl/', include('moduloETL.urls')),
    path('moduloETL/<path:subpath>', RedirectView.as_view(url='/etl/%(subpath)s', permanent=False)),
    path('moduloETL/', RedirectView.as_view(url='/etl/carga-nueva/', permanent=False)),
    path('dashboard/', include('dashboard.urls')),
    path('dashboard_predictivo/', RedirectView.as_view(pattern_name='dashboard:dashboard_predictivo', permanent=False), name='dashboard_predictivo_redirect'),
    path('dashboard-predictivo/', RedirectView.as_view(pattern_name='dashboard:dashboard_predictivo', permanent=False)),
    path('app/', include('AppWeb.urls')),
    path('', include('usuarios.urls')),
]   #path('', include('AppWeb.urls')),
