from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    ROL_DUENO = 'Dueño'
    ROL_CONTADOR = 'Contador'
    ROLES = [
        (ROL_DUENO, 'Dueño'),
        (ROL_CONTADOR, 'Contador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

class EstadoCarga(models.Model):
    """Fila única con los datos que el Contador cargó (CSV),
    visibles para el Dueño al ejecutar la predicción, sin depender de la sesión de cada usuario."""
    ruta_csv = models.CharField(max_length=500, null=True, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    @classmethod
    def actual(cls):
        estado, _ = cls.objects.get_or_create(pk=1)
        return estado

class Empresa(models.Model):
    rut = models.CharField(max_length=12, unique=True, help_text="RUT de la empresa")
    nombre = models.CharField(max_length=200)

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
