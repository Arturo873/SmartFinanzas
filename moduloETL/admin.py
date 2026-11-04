from django.contrib import admin
from .models import CargaFinanciera, RatioFinanciero


@admin.register(CargaFinanciera)
class CargaFinancieraAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'fecha_carga', 'tipo_carga', 'estado', 'usuario', 'empresa')
    list_filter = ('estado', 'tipo_carga', 'empresa')
    search_fields = ('periodo', 'archivo_origen')


@admin.register(RatioFinanciero)
class RatioFinancieroAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'fecha_calculo', 'v1_razon_corriente', 'v3_leverage_total', 'validado', 'empresa')
    list_filter = ('validado', 'empresa')
    search_fields = ('periodo',)
