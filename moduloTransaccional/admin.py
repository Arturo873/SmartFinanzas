from django.contrib import admin
from .models import MetodoPago, CierreCaja, DetalleCierrePorMetodo, RetiroCajaChica, Venta


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'comision_porcentaje', 'activo', 'empresa')
    list_filter = ('activo', 'empresa')
    search_fields = ('nombre',)


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'estado', 'total_sistema', 'total_arqueo', 'descuadre_total', 'cerrado_por_usuario', 'empresa')
    list_filter = ('estado', 'fecha', 'empresa')
    search_fields = ('fecha',)


@admin.register(DetalleCierrePorMetodo)
class DetalleCierrePorMetodoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cierre', 'metodo_pago', 'total_sistema', 'total_arqueo', 'descuadre')
    list_filter = ('metodo_pago',)


@admin.register(RetiroCajaChica)
class RetiroCajaChicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'monto', 'motivo', 'responsable', 'usuario', 'cierre', 'empresa')
    list_filter = ('empresa', 'fecha')
    search_fields = ('motivo', 'responsable')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'metodo_pago', 'total_bruto', 'total_cobrado', 'ingreso_real', 'usuario', 'cierre', 'empresa')
    list_filter = ('metodo_pago', 'fecha', 'empresa')
