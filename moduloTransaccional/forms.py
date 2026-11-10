from decimal import Decimal
from django import forms
from django.db.models import Q
from .models import Sale, PaymentMethod, CashRegisterClosure


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
                metodo = PaymentMethod.objects.filter(pk=pk).first()
                if metodo:
                    option['attrs']['data-comision'] = str(metodo.commission_percentage or 0)
            except Exception:
                pass
        return option


class VentaForm(forms.ModelForm):
    """
    Formulario de registro operativo de ventas.
    Valida que el total bruto sea mayor a 0 y que el descuento no consuma la venta.
    """
    discount_amount = forms.DecimalField(
        required=False,
        initial=Decimal('0.00'),
        min_value=Decimal('0.00'),
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_discount_amount',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label="Monto de Descuento ($)"
    )

    class Meta:
        model = Sale
        fields = ['payment_method', 'gross_total', 'discount_amount']
        widgets = {
            'payment_method': MetodoPagoSelect(attrs={
                'class': 'form-select',
                'id': 'id_payment_method'
            }),
            'gross_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_gross_total',
                'min': '1',
                'step': '0.01',
                'placeholder': 'Ej: 25000'
            }),
        }
        labels = {
            'payment_method': 'Método de Pago',
            'gross_total': 'Total Bruto ($)'
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo los métodos de pago activos pertenecientes a la empresa o globales
        metodos_qs = PaymentMethod.objects.filter(is_active=True)
        if empresa:
            metodos_qs = metodos_qs.filter(Q(company=empresa) | Q(company__isnull=True))
        self.fields['payment_method'].queryset = metodos_qs
        self.fields['payment_method'].empty_label = "-- Seleccione Método de Pago --"

    def clean_gross_total(self):
        gross_total = self.cleaned_data.get('gross_total')
        if gross_total is None:
            raise forms.ValidationError("El total bruto de la venta es obligatorio y no puede estar vacío.")
        if gross_total <= Decimal('0.00'):
            raise forms.ValidationError("El total bruto de la venta debe ser estrictamente mayor a 0.")
        if gross_total > Decimal('99999999.99'):
            raise forms.ValidationError("El total bruto excede el importe máximo permitido por transacción ($99.999.999,99).")
        return gross_total

    def clean_discount_amount(self):
        discount = self.cleaned_data.get('discount_amount')
        if discount is None:
            return Decimal('0.00')
        if discount < Decimal('0.00'):
            raise forms.ValidationError("El monto de descuento no puede ser un valor negativo.")
        return discount

    def clean_payment_method(self):
        metodo = self.cleaned_data.get('payment_method')
        if not metodo:
            raise forms.ValidationError("Debe seleccionar un método de pago válido.")
        if not metodo.is_active:
            raise forms.ValidationError(f"El método de pago '{metodo.name}' no está habilitado para operaciones.")
        return metodo

    def clean(self):
        cleaned_data = super().clean()
        gross_total = cleaned_data.get('gross_total')
        discount_amount = cleaned_data.get('discount_amount') or Decimal('0.00')

        if gross_total is not None and discount_amount is not None:
            if discount_amount >= gross_total:
                self.add_error(
                    'discount_amount',
                    forms.ValidationError(
                        f"El monto de descuento (${discount_amount:,.2f}) no puede ser mayor o igual "
                        f"al total bruto (${gross_total:,.2f}). El valor a cobrar resultante debe ser estrictamente mayor a 0."
                    )
                )
        return cleaned_data


class CierreCajaForm(forms.ModelForm):
    """
    Formulario de Cierre de Caja y Arqueo Diario.
    Controla la cuadratura física de gaveta (Efectivo) separada de la conciliación electrónica de tarjetas.
    """
    justification = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_justification',
            'rows': 3,
            'placeholder': 'Describa el motivo del descuadre detectado en gaveta (requerido si hay diferencia)...'
        }),
        label="Justificación de Descuadre en Gaveta",
        help_text="Requerido obligatoriamente si el dinero físico en gaveta no coincide con el efectivo esperado del sistema."
    )

    class Meta:
        model = CashRegisterClosure
        fields = ['counted_total']
        widgets = {
            'counted_total': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg fw-bold',
                'id': 'id_counted_total',
                'step': '0.01',
                'placeholder': 'Ej: 145000'
            })
        }
        labels = {
            'counted_total': 'Efectivo Físico en Gaveta ($)'
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

    def clean_counted_total(self):
        counted_total = self.cleaned_data.get('counted_total')
        if counted_total is None:
            raise forms.ValidationError("Debe ingresar el monto de efectivo físico contado en la gaveta.")
        if counted_total < Decimal('0.00'):
            raise forms.ValidationError("El total de efectivo físico no puede ser un valor negativo.")
        return counted_total

    def clean(self):
        cleaned_data = super().clean()
        counted_total = cleaned_data.get('counted_total')
        justification = (cleaned_data.get('justification') or '').strip()

        if counted_total is not None:
            if counted_total < Decimal('0.00'):
                self.add_error('counted_total', forms.ValidationError("El monto de efectivo físico no puede ser negativo."))
                return cleaned_data

            descuadre = counted_total - self.efectivo_esperado
            # Tolerancia contable para moneda sin centavos (CLP): diferencias menores a $1 peso se consideran cuadradas
            if abs(descuadre) < Decimal('1.00'):
                descuadre = Decimal('0.00')

            cleaned_data['descuadre_calculado'] = descuadre

            # Si hay descuadre en gaveta, la justificación es obligatoria
            if descuadre != Decimal('0.00'):
                if not justification:
                    signo = "+" if descuadre > Decimal('0.00') else "-"
                    self.add_error(
                        'justification',
                        forms.ValidationError(
                            f"Se ha detectado un descuadre en gaveta de {signo}${abs(descuadre):,.0f}. "
                            f"Debe justificar obligatoriamente el motivo de la diferencia para cerrar la caja."
                        )
                    )
        return cleaned_data

