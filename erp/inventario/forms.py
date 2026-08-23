from django import forms
from django.utils import timezone
from django.db.models import Sum

from .models import MovimientoInventario


class MovimientoInventarioForm(forms.ModelForm):
    manejo_lote = forms.BooleanField(required=False, label="Manejo por lotes")
    manejo_serie = forms.BooleanField(required=False, label="Manejo por serie")
    manejo_vencimiento = forms.BooleanField(required=False, label="Perecible (vencimiento)")

    cantidad = forms.DecimalField(
        min_value=1,
        max_digits=12,
        decimal_places=0,
        label="Cantidad",
        error_messages={
            "min_value": "La cantidad debe ser un número entero mayor a cero.",
            "invalid": "La cantidad debe ser un número entero.",
        },
    )

    # Campos avanzados (no obligatorios por defecto)
    lote = forms.CharField(
        required=False,
        min_length=3,
        max_length=30,
        label="Lote",
        error_messages={
            "min_length": "El lote debe tener al menos 3 caracteres.",
            "max_length": "El lote no puede superar los 30 caracteres.",
        },
    )

    serie = forms.CharField(
        required=False,
        min_length=3,
        max_length=30,
        label="Serie",
        error_messages={
            "min_length": "La serie debe tener al menos 3 caracteres.",
            "max_length": "La serie no puede superar los 30 caracteres.",
        },
    )

    observaciones = forms.CharField(
        required=False,
        min_length=5,
        max_length=300,
        label="Observaciones",
        widget=forms.Textarea(attrs={"rows": 3, "maxlength": 300}),
        error_messages={
            "min_length": "Las observaciones deben tener al menos 5 caracteres.",
            "max_length": "Las observaciones no pueden superar los 300 caracteres.",
        },
    )

    fecha_vencimiento = forms.DateField(
        required=False,
        label="Fecha de vencimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
        error_messages={
            "invalid": "Ingresa una fecha de vencimiento válida.",
        },
    )

    doc_referencia = forms.CharField(
        required=False,
        max_length=100,
        label="Documento de referencia",
    )

    motivo = forms.CharField(
        required=False,
        max_length=200,
        label="Motivo (ajustes / devoluciones)",
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            "tipo",
            "producto",
            "proveedor",
            "bodega_origen",
            "bodega_destino",
            "cantidad",
            # flags
            "manejo_lote",
            "manejo_serie",
            "manejo_vencimiento",
            # campos avanzados
            "lote",
            "serie",
            "fecha_vencimiento",
            "doc_referencia",
            "motivo",  
            "observaciones",
        ]

    # ---------- Validaciones individuales ----------

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get("fecha_vencimiento")
        manejo_venc = self.cleaned_data.get("manejo_vencimiento")

        # Solo valido si el checkbox está marcado
        if manejo_venc:
            if not fecha:
                raise forms.ValidationError("La fecha de vencimiento es obligatoria.")
            if fecha < timezone.localdate():
                raise forms.ValidationError(
                    "La fecha de vencimiento no puede ser anterior a hoy."
                )
        return fecha

    # ---------- Validaciones cruzadas ----------

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo")
        bodega_origen = cleaned_data.get("bodega_origen")
        bodega_destino = cleaned_data.get("bodega_destino")
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")

        manejo_lote = cleaned_data.get("manejo_lote")
        manejo_serie = cleaned_data.get("manejo_serie")
        manejo_vencimiento = cleaned_data.get("manejo_vencimiento")

        lote = cleaned_data.get("lote")
        serie = cleaned_data.get("serie")
        fecha_vencimiento = cleaned_data.get("fecha_vencimiento")

        # --- Reglas por tipo de movimiento ---
        if tipo == "TRANSFERENCIA":
            if not bodega_origen or not bodega_destino:
                raise forms.ValidationError(
                    "Para una transferencia debes indicar bodega origen y destino."
                )
            if bodega_origen == bodega_destino:
                raise forms.ValidationError(
                    "La bodega origen y destino no pueden ser la misma."
                )

        elif tipo == "INGRESO":
            if not bodega_destino:
                raise forms.ValidationError(
                    "Para un ingreso debes indicar la bodega destino."
                )

        elif tipo in ["SALIDA", "DEVOLUCION"]:
            if not bodega_origen:
                raise forms.ValidationError(
                    f"Para una {tipo.lower()} debes indicar la bodega origen."
                )

        # --- Validaciones ligadas a los toggles ---

        # Si manejo LOTE está activo, el lote se vuelve obligatorio
        if manejo_lote and not lote:
            self.add_error("lote", "El lote es obligatorio si activas manejo por lote.")

        # Si manejo SERIE está activo, la serie se vuelve obligatoria
        if manejo_serie and not serie:
            self.add_error("serie", "La serie es obligatoria si activas manejo por serie.")

        # Si manejo VENCIMIENTO está activo y no hay fecha, error (refuerzo)
        if manejo_vencimiento and not fecha_vencimiento:
            self.add_error(
                "fecha_vencimiento",
                "La fecha de vencimiento es obligatoria si el producto es perecible.",
            )
        # --- Validación de stock en bodega origen ---
        if (
            producto
            and cantidad
            and bodega_origen
            and tipo in ["SALIDA", "TRANSFERENCIA"]
        ):
            # Stock que HA ENTRADO a la bodega_origen
            ingresos_qs = MovimientoInventario.objects.filter(
                producto=producto,
                bodega_destino=bodega_origen,
                tipo__in=["INGRESO", "TRANSFERENCIA"],
            )

            # Stock que HA SALIDO de la bodega_origen
            salidas_qs = MovimientoInventario.objects.filter(
                producto=producto,
                bodega_origen=bodega_origen,
                tipo__in=["SALIDA", "TRANSFERENCIA"],
            )

            # Si estamos EDITANDO un movimiento, lo excluimos del cálculo
            if self.instance.pk:
                ingresos_qs = ingresos_qs.exclude(pk=self.instance.pk)
                salidas_qs = salidas_qs.exclude(pk=self.instance.pk)

            total_ingresos = ingresos_qs.aggregate(total=Sum("cantidad"))["total"] or 0
            total_salidas = salidas_qs.aggregate(total=Sum("cantidad"))["total"] or 0

            stock_actual = total_ingresos - total_salidas

            if cantidad > stock_actual:
                self.add_error(
                    "cantidad",
                    f"No hay stock suficiente en la bodega origen. "
                    f"Stock disponible: {stock_actual}, solicitado: {cantidad}.",
                )

        return cleaned_data
