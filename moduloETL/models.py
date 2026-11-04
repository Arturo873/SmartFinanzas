from django.db import models


class CargaFinanciera(models.Model):
    fecha_carga = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Carga")
    periodo = models.CharField(max_length=20, null=True, blank=True, verbose_name="Periodo")
    archivo_origen = models.CharField(max_length=255, null=True, blank=True, verbose_name="Archivo de Origen")
    tipo_carga = models.CharField(max_length=20, null=True, blank=True, verbose_name="Tipo de Carga")
    activo_corriente = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Activo Corriente"
    )
    pasivo_corriente = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Pasivo Corriente"
    )
    activo_total = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Activo Total"
    )
    pasivo_total = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Pasivo Total"
    )
    patrimonio = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Patrimonio"
    )
    ingresos_netos = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Ingresos Netos"
    )
    ebit = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="EBIT"
    )
    utilidades_retenidas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Utilidades Retenidas"
    )
    utilidad_neta = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Utilidad Neta"
    )
    inventarios = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Inventarios"
    )
    efectivo_equivalentes = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Efectivo y Equivalentes"
    )
    estado = models.CharField(max_length=30, null=True, blank=True, verbose_name="Estado")
    errores_detectados = models.TextField(null=True, blank=True, verbose_name="Errores Detectados")
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        related_name='cargas_financieras',
        verbose_name="Usuario"
    )
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='empresa_id',
        related_name='cargas_financieras',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'cargafinanciera'
        verbose_name = 'Carga Financiera'
        verbose_name_plural = 'Cargas Financieras'

    def __str__(self):
        return f"Carga {self.periodo} ({self.fecha_carga}) - {self.estado}"


class RatioFinanciero(models.Model):
    carga = models.ForeignKey(
        CargaFinanciera,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='carga_id',
        related_name='ratios',
        verbose_name="Carga Financiera"
    )
    periodo = models.CharField(max_length=20, null=True, blank=True, verbose_name="Periodo")
    fecha_calculo = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cálculo")
    
    # 7 Variables predictivas del modelo de Machine Learning
    v1_razon_corriente = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V1 - Razón Corriente"
    )
    v2_capital_trabajo_activos = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V2 - Capital Trabajo / Activos"
    )
    v3_leverage_total = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V3 - Leverage Total"
    )
    v4_roa_operacional = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V4 - ROA Operacional"
    )
    v5_margen_operacional = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V5 - Margen Operacional"
    )
    v6_rotacion_activos = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V6 - Rotación de Activos"
    )
    v7_volatilidad_flujo = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="V7 - Volatilidad del Flujo"
    )

    cierres_confirmados_count = models.IntegerField(
        null=True, blank=True, verbose_name="Cierres Confirmados Count"
    )
    usa_volatilidad_neutra = models.BooleanField(
        default=False, null=True, blank=True, verbose_name="Usa Volatilidad Neutra"
    )

    # Ratios de referencia contable
    ref_prueba_acida = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Prueba Ácida"
    )
    ref_razon_caja = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Razón de Caja"
    )
    ref_cobertura_operacional = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Cobertura Operacional"
    )
    ref_z_altman = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Ref - Z-Score Altman"
    )

    validado = models.BooleanField(default=False, null=True, blank=True, verbose_name="Validado")
    validado_por_usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='validado_por_usuario_id',
        related_name='ratios_validados',
        verbose_name="Validado Por"
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Validación")
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='empresa_id',
        related_name='ratios_financieros',
        verbose_name="Empresa"
    )

    class Meta:
        db_table = 'ratiofinanciero'
        verbose_name = 'Ratio Financiero'
        verbose_name_plural = 'Ratios Financieros'

    def __str__(self):
        return f"Ratios {self.periodo} ({self.fecha_calculo})"
