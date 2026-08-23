from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre de Categoría', unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']


class Producto(models.Model):
    sku = models.CharField(max_length=30, unique=True, verbose_name='SKU')
    ean_upc = models.CharField(max_length=30, blank=True, null=True, unique=True, verbose_name='Código EAN/UPC')
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Producto')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)

    uom_compra = models.CharField(max_length=10, default='UN', verbose_name='Unidad de Compra')
    uom_venta = models.CharField(max_length=10, default='UN', verbose_name='Unidad de Venta')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    costo_estandar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    costo_promedio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    impuesto_iva = models.PositiveIntegerField(default=19, verbose_name='IVA (%)')

    stock_minimo = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(blank=True, null=True)
    punto_reorden = models.PositiveIntegerField(blank=True, null=True)
    perishable = models.BooleanField(default=False, verbose_name='Perecible')
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)

    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name='Imagen del Producto')
    ficha_tecnica_url = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
