from django.contrib import admin
from .models import CargaFinanciera, RatioFinanciero


@admin.register(CargaFinanciera)
class CargaFinancieraAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'fecha_carga', 'tipo_carga', 'estado', 'usuario')
    list_filter = ('estado', 'tipo_carga')
    search_fields = ('periodo', 'archivo_origen')


@admin.register(RatioFinanciero)
class RatioFinancieroAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'fecha_calculo', 'v1_razon_corriente', 'v3_leverage_total', 'validado')
    list_filter = ('validado',)
    search_fields = ('periodo',)
