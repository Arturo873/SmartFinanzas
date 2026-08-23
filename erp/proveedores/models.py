from django.db import models
from django.utils import timezone
from .choices import CONDICIONES_PAGO, MONEDAS



class Pais(models.Model):
    nombre = models.CharField(max_length=64, verbose_name="Nombre País")
    codigo_iso = models.CharField(max_length=3, verbose_name="Código ISO (ej: CL, AR, BR)")

    class Meta:
        db_table = 'pais'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo_iso})"




class DivisionAdministrativa(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='divisiones')
    nombre = models.CharField(max_length=128, verbose_name="Nombre División")
    abreviacion = models.CharField(max_length=10, blank=True, null=True, verbose_name="Abreviación")
    codigo_oficial = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código Oficial")

    class Meta:
        db_table = 'division_administrativa'
        verbose_name = 'División Administrativa'
        verbose_name_plural = 'Divisiones Administrativas'
        unique_together = ('pais', 'nombre')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.pais.codigo_iso}"




class Proveedor(models.Model):
    rut_nif = models.CharField(max_length=20, unique=True, verbose_name='RUT / NIF')
    razon_social = models.CharField(max_length=255, verbose_name='Razón Social')
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nombre Fantasía')

    email = models.EmailField(verbose_name='Correo Electrónico')
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name='Teléfono')
    sitio_web = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sitio Web')

    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección')
    ciudad = models.CharField(max_length=128, blank=True, null=True, verbose_name='Ciudad')

    pais = models.ForeignKey(Pais, on_delete=models.SET_NULL, null=True, verbose_name="País")
    division = models.ForeignKey(
        DivisionAdministrativa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Región / Estado / Provincia / Depto"
    )

    condiciones_pago = models.CharField(
        max_length=50,
        choices=CONDICIONES_PAGO,
        verbose_name='Condiciones de Pago'
    )
    moneda = models.CharField(
        max_length=8,
        choices=MONEDAS,
        verbose_name='Moneda'
    )

    contacto_principal_nombre = models.CharField(max_length=120, blank=True, null=True, verbose_name="Nombre Contacto")
    contacto_principal_email = models.EmailField(blank=True, null=True, verbose_name="Email Contacto")
    contacto_principal_telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono Contacto")

    estado = models.CharField(
        max_length=10,
        choices=[('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado')],
        default='ACTIVO',
        verbose_name='Estado'
    )

    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name='Fecha Registro')

    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']

    def __str__(self):
        return f"{self.razon_social} ({self.rut_nif})"



class ProveedorProducto(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    producto = models.ForeignKey('catalogo.Producto', on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=18, decimal_places=6)
    lead_time_dias = models.PositiveIntegerField(default=7)
    min_lote = models.DecimalField(max_digits=18, decimal_places=6, default=1)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    preferente = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.proveedor.razon_social} → {self.producto.nombre}"

    class Meta:
        db_table = 'proveedor_producto'
        verbose_name = 'Producto por Proveedor'
        verbose_name_plural = 'Productos por Proveedor'
        unique_together = ('proveedor', 'producto')
