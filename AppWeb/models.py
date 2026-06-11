from django.db import models

class SectorIndustrial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    beta = models.FloatField(help_text="Coeficiente Beta del sector según modelo CAPM")

    def __str__(self):
        return f"{self.nombre} (Beta: {self.beta})"

class Empresa(models.Model):
    rut = models.CharField(max_length=12, unique=True, help_text="RUT de la empresa")
    nombre = models.CharField(max_length=200)
    sector = models.ForeignKey(SectorIndustrial, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

class HistorialPrediccion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(help_text="Puntaje probabilístico (0 a 100)")
    riesgo = models.CharField(max_length=20, choices=[
        ('Verde', 'Bajo'),
        ('Amarillo', 'Moderado'),
        ('Rojo', 'Crítico')
    ], help_text="Umbral de Alerta Temprana")

    # Guardar algunos ratios clave (opcional para justificación y trazabilidad)
    razon_corriente = models.FloatField(null=True, blank=True)
    prueba_acuda = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.empresa.nombre} - {self.fecha_prediccion.date()} - {self.riesgo}"
