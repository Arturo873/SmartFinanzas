from django.contrib import admin
from .models import MetodoPago, CierreCaja, DetalleCierrePorMetodo, RetiroCajaChica, Venta


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'comision_porcentaje', 'activo')
    list_filter = ('activo',)


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'estado', 'total_sistema', 'total_arqueo', 'descuadre_total', 'cerrado_por_usuario')
    list_filter = ('estado', 'fecha')
    search_fields = ('fecha',)


@admin.register(DetalleCierrePorMetodo)
class DetalleCierrePorMetodoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cierre', 'metodo_pago', 'total_sistema', 'total_arqueo', 'descuadre')
    list_filter = ('metodo_pago',)


@admin.register(RetiroCajaChica)
class RetiroCajaChicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'monto', 'motivo', 'responsable', 'usuario', 'cierre')
    search_fields = ('motivo', 'responsable')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'metodo_pago', 'total_bruto', 'total_cobrado', 'ingreso_real', 'usuario', 'cierre')
    list_filter = ('metodo_pago', 'fecha')
