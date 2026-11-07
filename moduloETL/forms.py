"""
Formularios para el Módulo ETL de SmartFinanzas.
"""

from django import forms


class CargaArchivoForm(forms.Form):
    """
    Formulario estandarizado para la subida y procesamiento de balances
    y estados financieros en formatos .csv o .xlsx.
    La empresa se asocia automáticamente a partir del usuario autenticado en sesión.
    """
    TIPO_CHOICES = [
        ('Balance General', 'Balance General (Estados Financieros IFRS)'),
        ('Estado de Resultados', 'Estado de Resultados (Ingresos, EBIT, Gastos)'),
    ]

    tipo_documento = forms.ChoiceField(
        choices=TIPO_CHOICES,
        initial='Balance General',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_tipo_documento'
        }),
        label="Tipo de Información Contable",
        help_text="Seleccione la categoría de información contable a procesar."
    )

    archivo_datos = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_archivo_datos',
            'accept': '.csv, .xlsx',
            'data-max-size': '26214400'
        }),
        label="Archivo de Estados Financieros (.csv, .xlsx)",
        help_text="Archivos admitidos: Planillas Excel (.xlsx) o archivos planos CSV delimitados por coma o punto y coma (máximo 25 MB)."
    )

    def clean_archivo_datos(self):
        archivo = self.cleaned_data.get('archivo_datos')
        if not archivo:
            raise forms.ValidationError("Debe seleccionar un archivo válido.")

        nombre = archivo.name.lower()
        if not (nombre.endswith('.csv') or nombre.endswith('.xlsx')):
            raise forms.ValidationError(
                "Formato no permitido. Solo se aceptan archivos con extensión .csv o .xlsx."
            )

        # Límite de tamaño: 25 MB (RNF-10)
        max_mb = 25
        if archivo.size > max_mb * 1024 * 1024:
            tamano_mb = archivo.size / (1024 * 1024)
            raise forms.ValidationError(
                f"El archivo pesa {tamano_mb:.2f} MB, superando el tamaño máximo permitido de {max_mb} MB (RNF-10)."
            )

        return archivo
