from django.db import models
from django.utils import timezone

from erp.catalogo.models import Producto
from erp.proveedores.models import Proveedor


class Bodega(models.Model):
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código Bodega")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Bodega")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        db_table = "bodega"
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"
        ordering = ["codigo"]


class EmbarqueImportacion(models.Model):
    codigo_bl = models.CharField(max_length=100, unique=True, verbose_name="Código BL / Tracking")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="embarques", verbose_name="Proveedor")
    incoterm = models.CharField(
        max_length=10,
        choices=[('FOB', 'FOB'), ('CIF', 'CIF'), ('EXW', 'EXW'), ('DDP', 'DDP')],
        verbose_name="Incoterm"
    )
    fecha_etd = models.DateField(blank=True, null=True, verbose_name="Fecha ETD (Salida Estimada)")
    fecha_eta = models.DateField(blank=True, null=True, verbose_name="Fecha ETA (Llegada Estimada)")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('EN_ORIGEN', 'En Origen'),
            ('EN_TRANSITO', 'En Tránsito'),
            ('EN_ADUANA', 'En Aduana'),
            ('RECIBIDO', 'Recibido en Bodega')
        ],
        default='EN_ORIGEN',
        verbose_name="Estado del Embarque"
    )
    costo_flete = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Costo Flete")
    costo_seguro = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Costo Seguro")
    impuestos_internacion = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Impuestos y Aranceles")
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo_bl} - {self.proveedor.razon_social}"

    class Meta:
        db_table = "embarque_importacion"
        verbose_name = "Embarque de Importación"
        verbose_name_plural = "Embarques de Importación"
        ordering = ["-fecha_eta"]


class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = (
        ("INGRESO", "Ingreso"),
        ("SALIDA", "Salida"),
        ("AJUSTE", "Ajuste"),
        ("DEVOLUCION", "Devolución"),
        ("TRANSFERENCIA", "Transferencia"),
    )

    tipo = models.CharField(
        max_length=15,
        choices=TIPO_MOVIMIENTO,
        verbose_name="Tipo de movimiento"
    )
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha")

    # Flags de control avanzado
    manejo_lote = models.BooleanField(default=False)
    manejo_serie = models.BooleanField(default=False)

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="movimientos",
        verbose_name="Producto"
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos",
        verbose_name="Proveedor"
    )

    embarque = models.ForeignKey(
        EmbarqueImportacion,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="movimientos",
        verbose_name="Embarque Asociado"
    )

    bodega_origen = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos_salida",
        verbose_name="Bodega origen"
    )
    bodega_destino = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos_ingreso",
        verbose_name="Bodega destino"
    )

    cantidad = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        verbose_name="Cantidad"
    )

    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Lote"
    )
    serie = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Serie"
    )
    contenedor = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Contenedor"
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    # 🔹 NUEVO: documento de referencia y motivo
    doc_referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Documento de referencia"
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Motivo (ajustes / devoluciones)"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"

    class Meta:
        db_table = "movimiento_inventario"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ["-fecha"]
