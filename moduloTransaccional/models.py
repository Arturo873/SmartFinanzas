from django.db import models


class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    comision_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Porcentaje de Comisión"
    )
    activo = models.BooleanField(default=True, null=True, blank=True, verbose_name="Activo")

    class Meta:
        db_table = 'metodopago'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'

    def __str__(self):
        return self.nombre


class CierreCaja(models.Model):
    fecha = models.DateField(unique=True, verbose_name="Fecha del Cierre")
    estado = models.CharField(max_length=15, null=True, blank=True, verbose_name="Estado")
    total_sistema = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Sistema"
    )
    total_retiros = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Retiros"
    )
    total_arqueo = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Arqueo"
    )
    descuadre_total = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Descuadre Total"
    )
    cerrado_por_usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='cerrado_por_usuario_id',
        related_name='cierres_realizados',
        verbose_name="Cerrado Por"
    )
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Confirmación")
    revisado_por_usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='revisado_por_usuario_id',
        related_name='cierres_revisados',
        verbose_name="Revisado Por"
    )
    fecha_revision = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Revisión")

    class Meta:
        db_table = 'cierrecaja'
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f"Cierre {self.fecha} - Estado: {self.estado}"


class DetalleCierrePorMetodo(models.Model):
    cierre = models.ForeignKey(
        CierreCaja,
        on_delete=models.CASCADE,
        db_column='cierre_id',
        related_name='detalles_metodo',
        verbose_name="Cierre de Caja"
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        db_column='metodo_pago_id',
        related_name='detalles_cierre',
        verbose_name="Método de Pago"
    )
    total_sistema = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Sistema"
    )
    total_arqueo = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Arqueo"
    )
    descuadre = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Descuadre"
    )
    justificacion = models.TextField(null=True, blank=True, verbose_name="Justificación")

    class Meta:
        db_table = 'detallecierrepormetodo'
        verbose_name = 'Detalle de Cierre por Método'
        verbose_name_plural = 'Detalles de Cierre por Método'

    def __str__(self):
        return f"Detalle Cierre #{self.cierre_id} - {self.metodo_pago.nombre}"


class RetiroCajaChica(models.Model):
    fecha = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora")
    monto = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto"
    )
    motivo = models.CharField(max_length=255, null=True, blank=True, verbose_name="Motivo")
    responsable = models.CharField(max_length=100, null=True, blank=True, verbose_name="Responsable")
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        related_name='retiros_caja_chica',
        verbose_name="Usuario"
    )
    cierre = models.ForeignKey(
        CierreCaja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='cierre_id',
        related_name='retiros',
        verbose_name="Cierre de Caja"
    )

    class Meta:
        db_table = 'retirocajachica'
        verbose_name = 'Retiro de Caja Chica'
        verbose_name_plural = 'Retiros de Caja Chica'

    def __str__(self):
        return f"Retiro ${self.monto} - {self.motivo} ({self.fecha})"


class Venta(models.Model):
    fecha = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Venta")
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='metodo_pago_id',
        related_name='ventas',
        verbose_name="Método de Pago"
    )
    total_bruto = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Bruto"
    )
    descuento_tipo = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="Tipo de Descuento"
    )
    descuento_monto = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto Descuento"
    )
    total_cobrado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Cobrado"
    )
    comision_aplicada = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Comisión Aplicada"
    )
    ingreso_real = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ingreso Real"
    )
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        related_name='ventas',
        verbose_name="Usuario"
    )
    cierre = models.ForeignKey(
        CierreCaja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='cierre_id',
        related_name='ventas',
        verbose_name="Cierre de Caja"
    )

    class Meta:
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta #{self.pk} - ${self.total_cobrado} ({self.fecha})"
