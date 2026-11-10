from django.db import models


class PaymentMethod(models.Model):  # Antes: MetodoPago
    name = models.CharField(max_length=50, verbose_name="Nombre")  # Antes: nombre
    commission_percentage = models.DecimalField(  # Antes: comision_porcentaje
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Porcentaje de Comisión"
    )
    is_active = models.BooleanField(default=True, null=True, blank=True, verbose_name="Activo")  # Antes: activo
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='payment_methods',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'payment_method'  # Antes: metodopago
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'

    def __str__(self):
        return self.name


class CashRegisterClosure(models.Model):  # Antes: CierreCaja
    date = models.DateField(unique=True, verbose_name="Fecha del Cierre")  # Antes: fecha
    status = models.CharField(max_length=15, null=True, blank=True, verbose_name="Estado")  # Antes: estado
    system_total = models.DecimalField(  # Antes: total_sistema
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Sistema"
    )
    withdrawals_total = models.DecimalField(  # Antes: total_retiros
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Retiros"
    )
    counted_total = models.DecimalField(  # Antes: total_arqueo
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Arqueo"
    )
    total_discrepancy = models.DecimalField(  # Antes: descuadre_total
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Descuadre Total"
    )
    closed_by_user = models.ForeignKey(  # Antes: cerrado_por_usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='closed_by_user_id',
        related_name='closures_performed',
        verbose_name="Cerrado Por"
    )
    confirmation_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Confirmación")  # Antes: fecha_confirmacion
    reviewed_by_user = models.ForeignKey(  # Antes: revisado_por_usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='reviewed_by_user_id',
        related_name='closures_reviewed',
        verbose_name="Revisado Por"
    )
    review_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Revisión")  # Antes: fecha_revision
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='cash_register_closures',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'cash_register_closure'  # Antes: cierrecaja
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f"Cierre {self.date} - Estado: {self.status}"


class ClosureMethodDetail(models.Model):  # Antes: DetalleCierrePorMetodo
    closure = models.ForeignKey(  # Antes: cierre
        CashRegisterClosure,
        on_delete=models.CASCADE,
        db_column='closure_id',
        related_name='method_details',
        verbose_name="Cierre de Caja"
    )
    payment_method = models.ForeignKey(  # Antes: metodo_pago
        PaymentMethod,
        on_delete=models.PROTECT,
        db_column='payment_method_id',
        related_name='closure_details',
        verbose_name="Método de Pago"
    )
    system_total = models.DecimalField(  # Antes: total_sistema
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Sistema"
    )
    counted_total = models.DecimalField(  # Antes: total_arqueo
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Arqueo"
    )
    discrepancy = models.DecimalField(  # Antes: descuadre
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Descuadre"
    )
    justification = models.TextField(null=True, blank=True, verbose_name="Justificación")  # Antes: justificacion

    class Meta:
        db_table = 'closure_method_detail'  # Antes: detallecierrepormetodo
        verbose_name = 'Detalle de Cierre por Método'
        verbose_name_plural = 'Detalles de Cierre por Método'

    def __str__(self):
        return f"Detalle Cierre #{self.closure_id} - {self.payment_method.name}"


class PettyCashWithdrawal(models.Model):  # Antes: RetiroCajaChica
    date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora")  # Antes: fecha
    amount = models.DecimalField(  # Antes: monto
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto"
    )
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Motivo")  # Antes: motivo
    responsible_person = models.CharField(max_length=100, null=True, blank=True, verbose_name="Responsable")  # Antes: responsable
    user = models.ForeignKey(  # Antes: usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',
        related_name='petty_cash_withdrawals',
        verbose_name="Usuario"
    )
    closure = models.ForeignKey(  # Antes: cierre
        CashRegisterClosure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='closure_id',
        related_name='withdrawals',
        verbose_name="Cierre de Caja"
    )
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='petty_cash_withdrawals',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'petty_cash_withdrawal'  # Antes: retirocajachica
        verbose_name = 'Retiro de Caja Chica'
        verbose_name_plural = 'Retiros de Caja Chica'

    def __str__(self):
        return f"Retiro ${self.amount} - {self.reason} ({self.date})"


class Sale(models.Model):  # Antes: Venta
    date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Venta")  # Antes: fecha
    payment_method = models.ForeignKey(  # Antes: metodo_pago
        PaymentMethod,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='payment_method_id',
        related_name='sales',
        verbose_name="Método de Pago"
    )
    gross_total = models.DecimalField(  # Antes: total_bruto
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Bruto"
    )
    discount_type = models.CharField(  # Antes: descuento_tipo
        max_length=10, null=True, blank=True, verbose_name="Tipo de Descuento"
    )
    discount_amount = models.DecimalField(  # Antes: descuento_monto
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto Descuento"
    )
    charged_total = models.DecimalField(  # Antes: total_cobrado
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Cobrado"
    )
    applied_commission = models.DecimalField(  # Antes: comision_aplicada
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Comisión Aplicada"
    )
    net_income = models.DecimalField(  # Antes: ingreso_real
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ingreso Real"
    )
    user = models.ForeignKey(  # Antes: usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',
        related_name='sales',
        verbose_name="Usuario"
    )
    closure = models.ForeignKey(  # Antes: cierre
        CashRegisterClosure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='closure_id',
        related_name='sales',
        verbose_name="Cierre de Caja"
    )
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='sales',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'sale'  # Antes: venta
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta #{self.pk} - ${self.charged_total} ({self.date})"
