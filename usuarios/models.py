from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Role(models.Model):  # Antes: Rol
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")  # Antes: nombre
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Descripción")  # Antes: descripcion

    class Meta:
        db_table = 'role'  # Antes: rol
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class Company(models.Model):  # Antes: Empresa
    business_name = models.CharField(max_length=200, verbose_name="Razón Social")  # Antes: razon_social
    tax_id = models.CharField(max_length=15, unique=True, verbose_name="RUT")  # Antes: rut
    business_sector = models.CharField(max_length=150, null=True, blank=True, verbose_name="Giro Comercial")  # Antes: giro
    debit_commission_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Comisión Débito (%)")  # Antes: comision_debito_pct
    credit_commission_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Comisión Crédito (%)")  # Antes: comision_credito_pct
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Actualización")  # Antes: fecha_actualizacion

    class Meta:
        db_table = 'company'  # Antes: empresa
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return f"{self.business_name} ({self.tax_id})"


class User(models.Model):  # Antes: Usuario
    username = models.CharField(max_length=50, unique=True, verbose_name="Nombre de Usuario")
    email = models.EmailField(max_length=100, verbose_name="Correo Electrónico")
    password_hash = models.CharField(max_length=255, verbose_name="Hash de Contraseña")
    role = models.ForeignKey(  # Antes: rol
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='role_id',
        related_name='users',
        verbose_name="Rol Asignado"
    )
    company = models.ForeignKey(  # Antes: empresa
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='users',
        verbose_name="Empresa"
    )
    is_active = models.BooleanField(default=True, null=True, blank=True, verbose_name="Activo")  # Antes: activo
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name="Fecha de Creación")  # Antes: fecha_creacion
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Última Sesión")  # Antes: ultima_sesion

    class Meta:
        db_table = 'user'  # Antes: usuario
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
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
