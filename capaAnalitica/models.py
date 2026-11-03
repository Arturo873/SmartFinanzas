from django.db import models


class PrediccionRiesgo(models.Model):
    ratio = models.ForeignKey(
        'moduloETL.RatioFinanciero',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='ratio_id',
        related_name='predicciones',
        verbose_name="Ratio Financiero Base"
    )
    fecha_prediccion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Predicción")
    score_riesgo = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Score de Riesgo (0-100)"
    )
    nivel_semaforo = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="Nivel de Semáforo (Verde/Amarillo/Rojo)"
    )
    variables_influyentes = models.TextField(
        null=True, blank=True, verbose_name="Variables Influyentes (JSON/Texto)"
    )
    impacto_variables = models.TextField(
        null=True, blank=True, verbose_name="Impacto de Variables (JSON/Texto)"
    )
    version_modelo = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Versión del Modelo ML"
    )
    tiempo_inferencia_ms = models.IntegerField(
        null=True, blank=True, verbose_name="Tiempo de Inferencia (ms)"
    )
    ejecutada_por_usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ejecutada_por_usuario_id',
        related_name='predicciones_ejecutadas',
        verbose_name="Ejecutada Por"
    )

    class Meta:
        db_table = 'prediccionriesgo'
        verbose_name = 'Predicción de Riesgo'
        verbose_name_plural = 'Predicciones de Riesgo'

    def __str__(self):
        return f"Predicción #{self.pk} - Score: {self.score_riesgo} ({self.nivel_semaforo})"


class Recomendacion(models.Model):
    prediccion = models.ForeignKey(
        PrediccionRiesgo,
        on_delete=models.CASCADE,
        db_column='prediccion_id',
        related_name='recomendaciones',
        verbose_name="Predicción de Riesgo"
    )
    variable_origen = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Variable de Origen"
    )
    grupo_riesgo = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Grupo de Riesgo"
    )
    texto = models.TextField(null=True, blank=True, verbose_name="Texto de la Recomendación")
    prioridad = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="Prioridad (Alta/Media/Baja)"
    )

    class Meta:
        db_table = 'recomendacion'
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'

    def __str__(self):
        return f"Recomendación [{self.prioridad}] - {self.variable_origen}"


class InformePDF(models.Model):
    prediccion = models.ForeignKey(
        PrediccionRiesgo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='prediccion_id',
        related_name='informes_pdf',
        verbose_name="Predicción Asociada"
    )
    fecha_generacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Generación")
    ruta_archivo = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="Ruta del Archivo PDF"
    )
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        related_name='informes_pdf_generados',
        verbose_name="Usuario Solicitante"
    )

    class Meta:
        db_table = 'informepdf'
        verbose_name = 'Informe PDF'
        verbose_name_plural = 'Informes PDF'

    def __str__(self):
        return f"Informe PDF #{self.pk} ({self.fecha_generacion})"
