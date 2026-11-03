from django.contrib import admin
from .models import PrediccionRiesgo, Recomendacion, InformePDF


@admin.register(PrediccionRiesgo)
class PrediccionRiesgoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_prediccion', 'score_riesgo', 'nivel_semaforo', 'version_modelo', 'ejecutada_por_usuario')
    list_filter = ('nivel_semaforo', 'version_modelo')


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'prediccion', 'variable_origen', 'grupo_riesgo', 'prioridad')
    list_filter = ('prioridad', 'grupo_riesgo')


@admin.register(InformePDF)
class InformePDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'prediccion', 'fecha_generacion', 'ruta_archivo', 'usuario')
    list_filter = ('fecha_generacion',)
