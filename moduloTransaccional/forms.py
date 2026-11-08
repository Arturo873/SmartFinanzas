from decimal import Decimal
from django import forms
from django.db.models import Q
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

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo los métodos de pago activos pertenecientes a la empresa o globales
        metodos_qs = MetodoPago.objects.filter(activo=True)
        if empresa:
            metodos_qs = metodos_qs.filter(Q(empresa=empresa) | Q(empresa__isnull=True))
        self.fields['metodo_pago'].queryset = metodos_qs
        self.fields['metodo_pago'].empty_label = "-- Seleccione Método de Pago --"

    def clean_total_bruto(self):
        total_bruto = self.cleaned_data.get('total_bruto')
        if total_bruto is None:
            raise forms.ValidationError("El total bruto de la venta es obligatorio y no puede estar vacío.")
        if total_bruto <= Decimal('0.00'):
            raise forms.ValidationError("El total bruto de la venta debe ser estrictamente mayor a 0.")
        if total_bruto > Decimal('99999999.99'):
            raise forms.ValidationError("El total bruto excede el importe máximo permitido por transacción ($99.999.999,99).")
        return total_bruto

    def clean_descuento_monto(self):
        descuento = self.cleaned_data.get('descuento_monto')
        if descuento is None:
            return Decimal('0.00')
        if descuento < Decimal('0.00'):
            raise forms.ValidationError("El monto de descuento no puede ser un valor negativo.")
        return descuento

    def clean_metodo_pago(self):
        metodo = self.cleaned_data.get('metodo_pago')
        if not metodo:
            raise forms.ValidationError("Debe seleccionar un método de pago válido.")
        if not metodo.activo:
            raise forms.ValidationError(f"El método de pago '{metodo.nombre}' no está habilitado para operaciones.")
        return metodo

    def clean(self):
        cleaned_data = super().clean()
        total_bruto = cleaned_data.get('total_bruto')
        descuento_monto = cleaned_data.get('descuento_monto') or Decimal('0.00')

        if total_bruto is not None and descuento_monto is not None:
            if descuento_monto >= total_bruto:
                self.add_error(
                    'descuento_monto',
                    forms.ValidationError(
                        f"El monto de descuento (${descuento_monto:,.2f}) no puede ser mayor o igual "
                        f"al total bruto (${total_bruto:,.2f}). El valor a cobrar resultante debe ser estrictamente mayor a 0."
                    )
                )
        return cleaned_data


class CierreCajaForm(forms.ModelForm):
    """
    Formulario de Cierre de Caja y Arqueo Diario.
    Controla la cuadratura física de gaveta (Efectivo) separada de la conciliación electrónica de tarjetas.
    """
    justificacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_justificacion',
            'rows': 3,
            'placeholder': 'Describa el motivo del descuadre detectado en gaveta (requerido si hay diferencia)...'
        }),
        label="Justificación de Descuadre en Gaveta",
        help_text="Requerido obligatoriamente si el dinero físico en gaveta no coincide con el efectivo esperado del sistema."
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
            'total_arqueo': 'Efectivo Físico en Gaveta ($)'
        }

    def __init__(self, *args, efectivo_esperado=None, total_sistema=None, total_electronico=None, **kwargs):
        if efectivo_esperado is not None:
            self.efectivo_esperado = Decimal(str(efectivo_esperado))
        elif total_sistema is not None:
            self.efectivo_esperado = Decimal(str(total_sistema))
        else:
            self.efectivo_esperado = Decimal('0.00')

        self.total_sistema = Decimal(str(total_sistema)) if total_sistema is not None else self.efectivo_esperado
        self.total_electronico = Decimal(str(total_electronico)) if total_electronico is not None else Decimal('0.00')
        super().__init__(*args, **kwargs)

    def clean_total_arqueo(self):
        total_arqueo = self.cleaned_data.get('total_arqueo')
        if total_arqueo is None:
            raise forms.ValidationError("Debe ingresar el monto de efectivo físico contado en la gaveta.")
        if total_arqueo < Decimal('0.00'):
            raise forms.ValidationError("El total de efectivo físico no puede ser un valor negativo.")
        return total_arqueo

    def clean(self):
        cleaned_data = super().clean()
        total_arqueo = cleaned_data.get('total_arqueo')
        justificacion = (cleaned_data.get('justificacion') or '').strip()

        if total_arqueo is not None:
            if total_arqueo < Decimal('0.00'):
                self.add_error('total_arqueo', forms.ValidationError("El monto de efectivo físico no puede ser negativo."))
                return cleaned_data

            descuadre = total_arqueo - self.efectivo_esperado
            # Tolerancia contable para moneda sin centavos (CLP): diferencias menores a $1 peso se consideran cuadradas
            if abs(descuadre) < Decimal('1.00'):
                descuadre = Decimal('0.00')

            cleaned_data['descuadre_calculado'] = descuadre

            # Si hay descuadre en gaveta, la justificación es obligatoria
            if descuadre != Decimal('0.00'):
                if not justificacion:
                    signo = "+" if descuadre > Decimal('0.00') else "-"
                    self.add_error(
                        'justificacion',
                        forms.ValidationError(
                            f"Se ha detectado un descuadre en gaveta de {signo}${abs(descuadre):,.0f}. "
                            f"Debe justificar obligatoriamente el motivo de la diferencia para cerrar la caja."
                        )
                    )
        return cleaned_data

