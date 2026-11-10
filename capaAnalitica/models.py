from django.db import models


class RiskPrediction(models.Model):  # Antes: PrediccionRiesgo
    ratio = models.ForeignKey(
        'moduloETL.FinancialRatio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='ratio_id',
        related_name='predictions',
        verbose_name="Ratio Financiero Base"
    )
    prediction_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Predicción")  # Antes: fecha_prediccion
    risk_score = models.DecimalField(  # Antes: score_riesgo
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Score de Riesgo (0-100)"
    )
    traffic_light_level = models.CharField(  # Antes: nivel_semaforo
        max_length=10, null=True, blank=True, verbose_name="Nivel de Semáforo (Verde/Amarillo/Rojo)"
    )
    influential_variables = models.TextField(  # Antes: variables_influyentes
        null=True, blank=True, verbose_name="Variables Influyentes (JSON/Texto)"
    )
    variable_impacts = models.TextField(  # Antes: impacto_variables
        null=True, blank=True, verbose_name="Impacto de Variables (JSON/Texto)"
    )
    model_version = models.CharField(  # Antes: version_modelo
        max_length=50, null=True, blank=True, verbose_name="Versión del Modelo ML"
    )
    inference_time_ms = models.IntegerField(  # Antes: tiempo_inferencia_ms
        null=True, blank=True, verbose_name="Tiempo de Inferencia (ms)"
    )
    executed_by_user = models.ForeignKey(  # Antes: ejecutada_por_usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='executed_by_user_id',
        related_name='executed_predictions',
        verbose_name="Ejecutada Por"
    )
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='risk_predictions',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'risk_prediction'  # Antes: prediccionriesgo
        verbose_name = 'Predicción de Riesgo'
        verbose_name_plural = 'Predicciones de Riesgo'

    def __str__(self):
        return f"Predicción #{self.pk} - Score: {self.risk_score} ({self.traffic_light_level})"


class Recommendation(models.Model):  # Antes: Recomendacion
    prediction = models.ForeignKey(  # Antes: prediccion
        RiskPrediction,
        on_delete=models.CASCADE,
        db_column='prediction_id',
        related_name='recommendations',
        verbose_name="Predicción de Riesgo"
    )
    source_variable = models.CharField(  # Antes: variable_origen
        max_length=50, null=True, blank=True, verbose_name="Variable de Origen"
    )
    risk_group = models.CharField(  # Antes: grupo_riesgo
        max_length=40, null=True, blank=True, verbose_name="Grupo de Riesgo"
    )
    text = models.TextField(null=True, blank=True, verbose_name="Texto de la Recomendación")  # Antes: texto
    priority = models.CharField(  # Antes: prioridad
        max_length=10, null=True, blank=True, verbose_name="Prioridad (Alta/Media/Baja)"
    )

    class Meta:
        db_table = 'recommendation'  # Antes: recomendacion
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'

    def __str__(self):
        return f"Recomendación [{self.priority}] - {self.source_variable}"


class PDFReport(models.Model):  # Antes: InformePDF
    prediction = models.ForeignKey(  # Antes: prediccion
        RiskPrediction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='prediction_id',
        related_name='pdf_reports',
        verbose_name="Predicción Asociada"
    )
    generation_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Generación")  # Antes: fecha_generacion
    file_path = models.CharField(  # Antes: ruta_archivo
        max_length=500, null=True, blank=True, verbose_name="Ruta del Archivo PDF"
    )
    user = models.ForeignKey(  # Antes: usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',
        related_name='generated_pdf_reports',
        verbose_name="Usuario Solicitante"
    )
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='pdf_reports',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'pdf_report'  # Antes: informepdf
        verbose_name = 'Informe PDF'
        verbose_name_plural = 'Informes PDF'

    def __str__(self):
        return f"Informe PDF #{self.pk} ({self.generation_date})"
