from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re

from .models import Proveedor, Pais, DivisionAdministrativa
from .choices import CONDICIONES_PAGO, MONEDAS


# --------------------------
# VALIDACIONES
# --------------------------
def validar_rut_nif(value):
    if len(value.strip()) < 8 or len(value.strip()) > 20:
        raise ValidationError("El RUT/NIF debe tener entre 8 y 20 caracteres.")
    if not re.match(r'^[0-9kK\.\-]+$', value):
        raise ValidationError("Formato inválido. Solo números, puntos y guiones.")


def validar_telefono(value):
    if not value:
        return
    if not re.match(r'^\d+$', value):
        raise ValidationError("El teléfono solo debe contener números.")
    if len(value) < 9 or len(value) > 15:
        raise ValidationError("El teléfono debe tener entre 9 y 15 dígitos.")


def validar_nombre(value):
    if len(value.strip()) < 3:
        raise ValidationError("Debe tener mínimo 3 caracteres.")
    if len(value.strip()) > 255:
        raise ValidationError("Ha excedido el máximo permitido (255 caracteres).")


def validar_moneda(value):
    # Ya no se usa directamente porque moneda es ChoiceField,
    # pero la dejamos por si en algún momento se requiere.
    if len(value) != 3:
        raise ValidationError("Debe tener exactamente 3 letras (ej: CLP, USD).")
    if not value.isalpha():
        raise ValidationError("Solo debe contener letras (ej: CLP).")


# --------------------------
# FORMULARIO PROVEEDOR
# --------------------------

class ProveedorForm(forms.ModelForm):

    # País como SELECT dinámico desde tabla Pais
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all().order_by("nombre"),
        required=True,
        label="País",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # División Administrativa (Región/Provincia/Estado)
    division = forms.ModelChoiceField(
        queryset=DivisionAdministrativa.objects.none(),
        required=False,  # si quieres forzar que siempre sea obligatorio → True
        label="Región / Estado / Provincia / Departamento",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # RUT
    rut_nif = forms.CharField(
        required=True,
        validators=[validar_rut_nif],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 11.111.111-1"
        })
    )

    # Razón Social
    razon_social = forms.CharField(
        required=True,
        validators=[validar_nombre],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Razón social completa"
        })
    )

    # Nombre Fantasía
    nombre_fantasia = forms.CharField(
        required=False,
        validators=[validar_nombre],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Opcional"
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "correo@empresa.cl"
        })
    )

    telefono = forms.CharField(
        required=False,
        validators=[validar_telefono],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Sólo números"
        })
    )

    sitio_web = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "https://www.ejemplo.cl"
        })
    )

    direccion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Calle 123, Oficina 45"
        })
    )

    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "La Serena"
        })
    )

    # Condiciones de pago → SELECT (desde choices.py)
    condiciones_pago = forms.ChoiceField(
        required=True,
        choices=CONDICIONES_PAGO,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Moneda → SELECT (desde choices.py)
    moneda = forms.ChoiceField(
        required=True,
        choices=MONEDAS,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Comentarios (opcional)"
        })
    )

    class Meta:
        model = Proveedor
        fields = [
            "rut_nif", "razon_social", "nombre_fantasia",
            "email", "telefono", "sitio_web",
            "direccion", "ciudad", "pais", "division",
            "condiciones_pago", "moneda",
            "contacto_principal_nombre", "contacto_principal_email",
            "contacto_principal_telefono",
            "estado", "observaciones"
        ]

        widgets = {
            "contacto_principal_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_principal_email": forms.EmailInput(attrs={"class": "form-control"}),
            "contacto_principal_telefono": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    # --------------------------
    # INICIALIZACIÓN (para AJAX)
    # --------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # por defecto, sin país seleccionado, dejamos el queryset vacío
        self.fields["division"].queryset = DivisionAdministrativa.objects.none()

        # 1) Si viene de un POST con país elegido
        if "pais" in self.data:
            try:
                pais_id = int(self.data.get("pais"))
                self.fields["division"].queryset = DivisionAdministrativa.objects.filter(
                    pais_id=pais_id
                ).order_by("nombre")
            except (ValueError, TypeError):
                pass

        # 2) Si estamos editando un proveedor existente
        elif self.instance.pk and self.instance.pais:
            self.fields["division"].queryset = DivisionAdministrativa.objects.filter(
                pais=self.instance.pais
            ).order_by("nombre")
            # set iniciales por si acaso
            self.initial.setdefault("pais", self.instance.pais)
            if self.instance.division:
                self.initial.setdefault("division", self.instance.division)

    # --------------------------
    # LIMPIEZAS EXTRA
    # --------------------------

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = Proveedor.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un proveedor registrado con este correo.")
        return email

    def clean_sitio_web(self):
        sitio = self.cleaned_data.get("sitio_web")
        if sitio:
            validate_url = URLValidator()
            try:
                validate_url(sitio)
            except Exception:
                raise ValidationError("Debe ingresar una URL válida.")
        return sitio

    def clean_rut_nif(self):
        rut = self.cleaned_data.get("rut_nif")
        qs = Proveedor.objects.filter(rut_nif=rut)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un proveedor con este RUT/NIF.")
        return rut
