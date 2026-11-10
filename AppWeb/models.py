from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):  # Antes: PerfilUsuario
    OWNER_ROLE = 'Dueño'
    ACCOUNTANT_ROLE = 'Contador'
    ROLE_CHOICES = [
        (OWNER_ROLE, 'Dueño'),
        (ACCOUNTANT_ROLE, 'Contador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  # Antes: rol

    class Meta:
        db_table = 'user_profile'  # Antes: appweb_perfilusuario

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class UploadState(models.Model):  # Antes: EstadoCarga
    """Fila única con los datos que el Contador cargó (CSV),
    visibles para el Dueño al ejecutar la predicción, sin depender de la sesión de cada usuario."""
    csv_path = models.CharField(max_length=500, null=True, blank=True)  # Antes: ruta_csv
    updated_at = models.DateTimeField(auto_now=True)  # Antes: actualizado_en

    class Meta:
        db_table = 'upload_state'  # Antes: appweb_estadocarga

    @classmethod
    def current(cls):
        state, _ = cls.objects.get_or_create(pk=1)
        return state


class Company(models.Model):  # Antes: Empresa
    tax_id = models.CharField(max_length=12, unique=True, help_text="RUT de la empresa")  # Antes: rut
    name = models.CharField(max_length=200)  # Antes: nombre

    class Meta:
        db_table = 'appweb_company'  # Antes: appweb_empresa

    def __str__(self):
        return self.name


class PredictionHistory(models.Model):  # Antes: HistorialPrediccion
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Antes: empresa
    prediction_date = models.DateTimeField(auto_now_add=True)  # Antes: fecha_prediccion
    score = models.FloatField(help_text="Puntaje probabilístico (0 a 100)")
    risk = models.CharField(max_length=20, choices=[  # Antes: riesgo
        ('Verde', 'Bajo'),
        ('Amarillo', 'Moderado'),
        ('Rojo', 'Crítico')
    ], help_text="Umbral de Alerta Temprana")

    # Guardar algunos ratios clave (opcional para justificación y trazabilidad)
    current_ratio = models.FloatField(null=True, blank=True)  # Antes: razon_corriente
    quick_ratio = models.FloatField(null=True, blank=True)  # Antes: prueba_acuda

    class Meta:
        db_table = 'prediction_history'  # Antes: appweb_historialprediccion

    def __str__(self):
        return f"{self.company.name} - {self.prediction_date.date()} - {self.risk}"
