from django.contrib import admin
from .models import Rol, Empresa, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'razon_social', 'rut', 'giro', 'comision_debito_pct', 'comision_credito_pct')
    search_fields = ('razon_social', 'rut')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'rol', 'empresa', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'rol')
    search_fields = ('username', 'email')
