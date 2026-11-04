from decimal import Decimal
from django import forms
from .models import Venta, MetodoPago, CierreCaja


class MetodoPagoSelect(forms.Select):
    """
    Widget personalizado que inyecta el atributo 'data-comision' en cada <option>.
    Permite al JavaScript del frontend calcular la comisión en tiempo real.
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:
            try:
                pk = value.value if hasattr(value, 'value') else value
                metodo = MetodoPago.objects.filter(pk=pk).first()
                if metodo:
                    option['attrs']['data-comision'] = str(metodo.comision_porcentaje or 0)
            except Exception:
                pass
        return option


class VentaForm(forms.ModelForm):
    """
    Formulario de registro operativo de ventas.
    Valida que el total bruto sea mayor a 0 y que el descuento no consuma la venta.
    """
    descuento_monto = forms.DecimalField(
        required=False,
        initial=Decimal('0.00'),
        min_value=Decimal('0.00'),
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_descuento_monto',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label="Monto de Descuento ($)"
    )

    class Meta:
        model = Venta
        fields = ['metodo_pago', 'total_bruto', 'descuento_monto']
        widgets = {
            'metodo_pago': MetodoPagoSelect(attrs={
                'class': 'form-select',
                'id': 'id_metodo_pago'
            }),
            'total_bruto': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_total_bruto',
                'min': '1',
                'step': '0.01',
                'placeholder': 'Ej: 25000'
            }),
        }
        labels = {
            'metodo_pago': 'Método de Pago',
            'total_bruto': 'Total Bruto ($)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo los métodos de pago activos
        self.fields['metodo_pago'].queryset = MetodoPago.objects.filter(activo=True)
        self.fields['metodo_pago'].empty_label = "-- Seleccione Método de Pago --"

    def clean_total_bruto(self):
        total_bruto = self.cleaned_data.get('total_bruto')
        if total_bruto is not None and total_bruto <= Decimal('0.00'):
            raise forms.ValidationError("El total bruto de la venta debe ser estrictamente mayor a 0.")
        return total_bruto

    def clean(self):
        cleaned_data = super().clean()
        total_bruto = cleaned_data.get('total_bruto')
        descuento_monto = cleaned_data.get('descuento_monto') or Decimal('0.00')

        if total_bruto is not None and descuento_monto is not None:
            if descuento_monto < Decimal('0.00'):
                self.add_error('descuento_monto', forms.ValidationError("El descuento no puede ser un valor negativo."))
            elif descuento_monto >= total_bruto:
                self.add_error(
                    'descuento_monto',
                    forms.ValidationError("El monto de descuento no puede ser mayor o igual al total bruto de la venta.")
                )
        return cleaned_data


class CierreCajaForm(forms.ModelForm):
    """
    Formulario de Cierre de Caja y Arqueo Diario.
    Recibe el 'total_sistema' por kwargs y fuerza la justificación si hay descuadre.
    """
    justificacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_justificacion',
            'rows': 3,
            'placeholder': 'Describa el motivo del descuadre detectado (requerido si hay diferencia)...'
        }),
        label="Justificación de Descuadre",
        help_text="Requerido obligatoriamente si el dinero en arqueo no coincide con el total del sistema."
    )

    class Meta:
        model = CierreCaja
        fields = ['total_arqueo']
        widgets = {
            'total_arqueo': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg fw-bold',
                'id': 'id_total_arqueo',
                'step': '0.01',
                'placeholder': 'Ej: 145000'
            })
        }
        labels = {
            'total_arqueo': 'Total Arqueo Físico ($)'
        }

    def __init__(self, *args, total_sistema=None, **kwargs):
        self.total_sistema = total_sistema if total_sistema is not None else Decimal('0.00')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        total_arqueo = cleaned_data.get('total_arqueo')
        justificacion = (cleaned_data.get('justificacion') or '').strip()

        if total_arqueo is not None:
            if total_arqueo < Decimal('0.00'):
                self.add_error('total_arqueo', forms.ValidationError("El monto de arqueo físico no puede ser negativo."))
                return cleaned_data

            descuadre = total_arqueo - self.total_sistema
            cleaned_data['descuadre_calculado'] = descuadre

            # Si hay descuadre matemático, la justificación es obligatoria
            if descuadre != Decimal('0.00'):
                if not justificacion:
                    signo = "+" if descuadre > 0 else "-"
                    self.add_error(
                        'justificacion',
                        forms.ValidationError(
                            f"Se ha detectado un descuadre de {signo}${abs(descuadre):,.2f}. "
                            f"Debe justificar obligatoriamente el motivo de la diferencia para cerrar la caja."
                        )
                    )
        return cleaned_data

