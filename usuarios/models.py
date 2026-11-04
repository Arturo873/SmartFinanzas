from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    descripcion = models.CharField(max_length=255, null=True, blank=True, verbose_name="Descripción")

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    razon_social = models.CharField(max_length=200, verbose_name="Razón Social")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT")
    giro = models.CharField(max_length=150, null=True, blank=True, verbose_name="Giro Comercial")
    comision_debito_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Comisión Débito (%)")
    comision_credito_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Comisión Crédito (%)")
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Actualización")

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return f"{self.razon_social} ({self.rut})"


# Alias para retrocompatibilidad
ConfiguracionEmpresa = Empresa


class Usuario(models.Model):
    username = models.CharField(max_length=50, unique=True, verbose_name="Nombre de Usuario")
    email = models.EmailField(max_length=100, verbose_name="Correo Electrónico")
    password_hash = models.CharField(max_length=255, verbose_name="Hash de Contraseña")
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='rol_id',
        related_name='usuarios',
        verbose_name="Rol Asignado"
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='empresa_id',
        related_name='usuarios',
        verbose_name="Empresa"
    )
    activo = models.BooleanField(default=True, null=True, blank=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name="Fecha de Creación")
    ultima_sesion = models.DateTimeField(null=True, blank=True, verbose_name="Última Sesión")

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def save(self, *args, **kwargs):
        if not self.fecha_creacion:
            self.fecha_creacion = timezone.now()
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password_hash or not raw_password:
            return False
        try:
            return check_password(raw_password, self.password_hash)
        except Exception:
            return False

    def __str__(self):
        return self.username
