from django.db import models


class FinancialUpload(models.Model):  # Antes: CargaFinanciera
    upload_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Carga")  # Antes: fecha_carga
    period = models.CharField(max_length=20, null=True, blank=True, verbose_name="Periodo")  # Antes: periodo
    source_file = models.CharField(max_length=255, null=True, blank=True, verbose_name="Archivo de Origen")  # Antes: archivo_origen
    upload_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="Tipo de Carga")  # Antes: tipo_carga
    current_assets = models.DecimalField(  # Antes: activo_corriente
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Activo Corriente"
    )
    current_liabilities = models.DecimalField(  # Antes: pasivo_corriente
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Pasivo Corriente"
    )
    total_assets = models.DecimalField(  # Antes: activo_total
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Activo Total"
    )
    total_liabilities = models.DecimalField(  # Antes: pasivo_total
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Pasivo Total"
    )
    equity = models.DecimalField(  # Antes: patrimonio
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Patrimonio"
    )
    net_revenue = models.DecimalField(  # Antes: ingresos_netos
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Ingresos Netos"
    )
    ebit = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="EBIT"
    )
    retained_earnings = models.DecimalField(  # Antes: utilidades_retenidas
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Utilidades Retenidas"
    )
    net_income = models.DecimalField(  # Antes: utilidad_neta
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Utilidad Neta"
    )
    inventories = models.DecimalField(  # Antes: inventarios
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Inventarios"
    )
    cash_and_equivalents = models.DecimalField(  # Antes: efectivo_equivalentes
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Efectivo y Equivalentes"
    )
    status = models.CharField(max_length=30, null=True, blank=True, verbose_name="Estado")  # Antes: estado
    detected_errors = models.TextField(null=True, blank=True, verbose_name="Errores Detectados")  # Antes: errores_detectados
    user = models.ForeignKey(  # Antes: usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',
        related_name='financial_uploads',
        verbose_name="Usuario"
    )
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='financial_uploads',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'financial_upload'  # Antes: cargafinanciera
        verbose_name = 'Carga Financiera'
        verbose_name_plural = 'Cargas Financieras'

    def __str__(self):
        return f"Carga {self.period} ({self.upload_date}) - {self.status}"


class FinancialRatio(models.Model):  # Antes: RatioFinanciero
    upload = models.ForeignKey(  # Antes: carga
        FinancialUpload,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='upload_id',
        related_name='ratios',
        verbose_name="Carga Financiera"
    )
    period = models.CharField(max_length=20, null=True, blank=True, verbose_name="Periodo")  # Antes: periodo
    calculation_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cálculo")  # Antes: fecha_calculo
    
    # 7 Variables predictivas del modelo de Machine Learning
    v1_current_ratio = models.DecimalField(  # Antes: v1_razon_corriente
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V1 - Razón Corriente"
    )
    v2_working_capital_to_assets = models.DecimalField(  # Antes: v2_capital_trabajo_activos
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V2 - Capital Trabajo / Activos"
    )
    v3_total_leverage = models.DecimalField(  # Antes: v3_leverage_total
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V3 - Leverage Total"
    )
    v4_operating_roa = models.DecimalField(  # Antes: v4_roa_operacional
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V4 - ROA Operacional"
    )
    v5_operating_margin = models.DecimalField(  # Antes: v5_margen_operacional
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V5 - Margen Operacional"
    )
    v6_asset_turnover = models.DecimalField(  # Antes: v6_rotacion_activos
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V6 - Rotación de Activos"
    )
    v7_cash_flow_volatility = models.DecimalField(  # Antes: v7_volatilidad_flujo
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V7 - Volatilidad del Flujo"
    )

    confirmed_closures_count = models.IntegerField(  # Antes: cierres_confirmados_count
        null=True, blank=True, verbose_name="Cierres Confirmados Count"
    )
    uses_neutral_volatility = models.BooleanField(  # Antes: usa_volatilidad_neutra
        default=False, null=True, blank=True, verbose_name="Usa Volatilidad Neutra"
    )

    # Ratios de referencia contable
    ref_quick_ratio = models.DecimalField(  # Antes: ref_prueba_acida
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Prueba Ácida"
    )
    ref_cash_ratio = models.DecimalField(  # Antes: ref_razon_caja
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Razón de Caja"
    )
    ref_operating_coverage = models.DecimalField(  # Antes: ref_cobertura_operacional
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Cobertura Operacional"
    )
    ref_altman_z_score = models.DecimalField(  # Antes: ref_z_altman
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Z-Score Altman"
    )

    is_validated = models.BooleanField(default=False, null=True, blank=True, verbose_name="Validado")  # Antes: validado
    validated_by_user = models.ForeignKey(  # Antes: validado_por_usuario
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='validated_by_user_id',
        related_name='validated_ratios',
        verbose_name="Validado Por"
    )
    validation_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Validación")  # Antes: fecha_validacion
    company = models.ForeignKey(  # Antes: empresa
        'usuarios.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='company_id',
        related_name='financial_ratios',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'financial_ratio'  # Antes: ratiofinanciero
        verbose_name = 'Ratio Financiero'
        verbose_name_plural = 'Ratios Financieros'

    def __str__(self):
        return f"Ratios {self.period} ({self.calculation_date})"
