from django import forms
from django.core.exceptions import ValidationError
from .models import Categoria, Producto
import re


def validar_solo_numeros(value):
    if not re.match(r'^\d+$', value):
        raise ValidationError('Este campo solo puede contener números.')

def validar_ean_upc(value):
    if value and isinstance(value, str):
        value = value.strip()
        if not re.match(r'^\d{8}$|^\d{12,13}$', value):
            raise ValidationError("Código EAN/UPC inválido. Debe tener 8, 12 o 13 dígitos.")
    return value





class ProductoForm(forms.ModelForm):


    sku = forms.CharField(
        max_length=16,
        min_length=4,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: CK-0023-R"
        })
    )

    ean_upc = forms.CharField(
        required=False,
        validators=[validar_ean_upc],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 7501031130001 (opcional)"
        })
    )

    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombre del producto"
        })
    )

    descripcion = forms.CharField(
        required=True,
        min_length=10,
        max_length=4000,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "class": "form-control",
            "placeholder": "Descripción del producto"
        })
    )

    marca = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    modelo = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    UOM_OPCIONES = [
        ("UN", "Unidad"),
        ("CAJA", "Caja"),
        ("PACK", "Pack"),
        ("KG", "Kilogramo"),
        ("G", "Gramos"),
        ("LTS", "Litros"),
    ]

    uom_compra = forms.ChoiceField(
        choices=UOM_OPCIONES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    uom_venta = forms.ChoiceField(
        choices=UOM_OPCIONES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    factor_conversion = forms.DecimalField(
        min_value=1,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    costo_estandar = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    costo_promedio = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    precio_venta = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    impuesto_iva = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=19,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    stock_minimo = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    stock_maximo = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    punto_reorden = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    perishable = forms.BooleanField(required=False)
    control_por_lote = forms.BooleanField(required=False)
    control_por_serie = forms.BooleanField(required=False)

    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    imagen = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    ficha_tecnica_url = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "URL o nombre del archivo PDF"
        })
    )

    class Meta:
        model = Producto
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        stock_min = cleaned_data.get("stock_minimo")
        stock_max = cleaned_data.get("stock_maximo")
        punto_reorden = cleaned_data.get("punto_reorden")

        if stock_max is not None and stock_min is not None and stock_max < stock_min:
            raise ValidationError("El stock máximo no puede ser menor al stock mínimo.")

        if punto_reorden and stock_max and punto_reorden > stock_max:
            raise ValidationError("El punto de reorden no puede ser mayor al stock máximo.")
