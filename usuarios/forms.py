from django import forms
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import Usuario, Rol, Empresa, ConfiguracionEmpresa


class LoginForm(forms.Form):
    """
    Formulario de autenticación que valida credenciales directamente contra la tabla 'usuario' (BDD).
    Inicia sesión exclusivamente mediante correo electrónico.
    """
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'correo@empresa.cl',
            'autofocus': True,
            'required': True
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('email') or '').strip().lower()
        password = cleaned_data.get('password')

        if email and password:
            # Autenticación exclusiva por correo electrónico
            usuario = Usuario.objects.filter(
                email__iexact=email
            ).select_related('rol', 'empresa').first()

            # Mensaje de error general para no revelar si falló el correo o la contraseña
            if not usuario or not usuario.check_password(password):
                raise forms.ValidationError("Correo electrónico o contraseña incorrectos. Por favor verifique sus datos.")

            if not usuario.activo:
                raise forms.ValidationError("Esta cuenta de usuario se encuentra inactiva. Contacte al Administrador.")

            cleaned_data['usuario_db'] = usuario

        return cleaned_data


class RegistroForm(forms.ModelForm):
    """
    Formulario de registro de nuevas cuentas persistiendo directamente en la BDD (tabla 'usuario').
    """
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 4 caracteres',
            'required': True
        })
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
            'required': True
        })
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        empty_label="-- Selecciona tu Rol --",
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
        label="Rol en la Empresa"
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        required=False,
        empty_label="-- Selecciona Empresa (Opcional) --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Empresa Asociada"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'empresa']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: jperezo',
                'autofocus': True,
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@empresa.cl',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si no existen roles en la BDD, asegurar los roles por defecto
        if Rol.objects.count() == 0:
            roles_base = [
                ('Dueño', 'Gerencia, visualización de dashboard y arqueos de caja'),
                ('Contador', 'Carga de planillas ETL, predicciones y revisión contable'),
                ('Trabajador', 'Registro de ventas operativas'),
                ('Administrador', 'Gestión técnica y permisos')
            ]
            for nombre, desc in roles_base:
                Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            self.fields['rol'].queryset = Rol.objects.all()

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está registrado en la base de datos.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está asociado a otra cuenta.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', forms.ValidationError("Las contraseñas no coinciden."))
            elif len(password) < 4:
                self.add_error('password', forms.ValidationError("La contraseña debe tener al menos 4 caracteres."))

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data['password']
        usuario.set_password(password)
        usuario.activo = True
        if not usuario.fecha_creacion:
            usuario.fecha_creacion = timezone.now()

        # Asignar primera empresa por defecto si no seleccionó ninguna
        if not usuario.empresa:
            usuario.empresa = Empresa.objects.first()

        if commit:
            usuario.save()
        return usuario

