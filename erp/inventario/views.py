from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook
from .models import MovimientoInventario, EmbarqueImportacion
from .forms import MovimientoInventarioForm, EmbarqueImportacionForm
from django.utils import timezone

def movimientos_listar(request):
    movimientos = MovimientoInventario.objects.select_related(
        "producto", "proveedor", "bodega_origen", "bodega_destino"
    ).all()
    # Mocking permisos as True for all, since we removed roles for now
    permisos = {"inventario_crear": True, "inventario_editar": True, "inventario_eliminar": True}
    return render(request, "erp/mantenedores/inventario/movimientos_listar.html", {
        "movimientos": movimientos, "permisos": permisos,
    })

def movimiento_crear(request):
    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save()
            messages.success(request, "✅ Movimiento de inventario registrado correctamente.")
            return redirect("erp_movimientos_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = MovimientoInventarioForm()
    permisos = {"inventario_crear": True, "inventario_editar": True, "inventario_eliminar": True}
    return render(request, "erp/mantenedores/inventario/movimiento_form.html", {
        "form": form, "permisos": permisos,
    })

def movimiento_editar(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    fecha_original = movimiento.fecha  
    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST, instance=movimiento)
        if form.is_valid():
            movimiento_editado = form.save(commit=False)
            movimiento_editado.fecha = fecha_original 
            movimiento_editado.save()
            messages.success(request, "✅ Movimiento de inventario actualizado correctamente.")
            return redirect("erp_movimientos_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = MovimientoInventarioForm(instance=movimiento)
    permisos = {"inventario_crear": True, "inventario_editar": True, "inventario_eliminar": True}
    return render(request, "erp/mantenedores/inventario/movimiento_form.html", {
        "form": form, "permisos": permisos,
    })

def movimiento_eliminar(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    if request.method == "POST":
        movimiento.delete()
        messages.success(request, "✅ Movimiento de inventario eliminado correctamente.")
        return redirect("erp_movimientos_listar")
    permisos = {"inventario_crear": True, "inventario_editar": True, "inventario_eliminar": True}
    return render(request, "erp/mantenedores/inventario/movimiento_confirmar_eliminar.html", {
        "movimiento": movimiento, "permisos": permisos,
    })

def exportar_movimientos_excel(request):
    movimientos = (
        MovimientoInventario.objects
        .select_related("producto", "proveedor", "bodega_origen", "bodega_destino")
        .order_by("-fecha")
    )   
    wb = Workbook()
    ws = wb.active
    ws.title = "Movimientos"
    encabezados = [
        "ID", "Fecha registro", "Tipo", "Producto", "Proveedor (RUT/NIF)",
        "Bodega origen", "Bodega destino", "Cantidad", "Lote", "Serie",
        "Fecha vencimiento", "Documento referencia", "Motivo", "Observaciones"
    ]
    ws.append(encabezados)
    for m in movimientos:
        ws.append([
            m.id,
            m.fecha.strftime("%d-%m-%Y %H:%M") if m.fecha else "",
            m.get_tipo_display(),
            m.producto.nombre if m.producto else "",
            m.proveedor.rut_nif if m.proveedor else "",
            m.bodega_origen.nombre if m.bodega_origen else "",
            m.bodega_destino.nombre if m.bodega_destino else "",
            float(m.cantidad) if m.cantidad is not None else "",
            m.lote or "",
            m.serie or "",
            m.fecha_vencimiento.strftime("%d-%m-%Y") if m.fecha_vencimiento else "",
            m.doc_referencia or "",
            m.motivo or "",
            m.observaciones or "",
        ])
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="movimientos_inventario.xlsx"'
    wb.save(response)
    return response


# --- Vistas para Embarques de Importación ---

def embarques_listar(request):
    embarques = EmbarqueImportacion.objects.select_related("proveedor").order_by("-fecha_eta")
    permisos = {"embarque_crear": True, "embarque_editar": True, "embarque_eliminar": True}
    return render(request, "erp/mantenedores/inventario/embarques_listar.html", {
        "embarques": embarques, "permisos": permisos,
    })

def embarque_crear(request):
    if request.method == "POST":
        form = EmbarqueImportacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Embarque registrado correctamente.")
            return redirect("erp_embarques_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = EmbarqueImportacionForm()
    permisos = {"embarque_crear": True, "embarque_editar": True, "embarque_eliminar": True}
    return render(request, "erp/mantenedores/inventario/embarque_form.html", {
        "form": form, "permisos": permisos,
    })

def embarque_editar(request, pk):
    embarque = get_object_or_404(EmbarqueImportacion, pk=pk)
    if request.method == "POST":
        form = EmbarqueImportacionForm(request.POST, instance=embarque)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Embarque actualizado correctamente.")
            return redirect("erp_embarques_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = EmbarqueImportacionForm(instance=embarque)
    permisos = {"embarque_crear": True, "embarque_editar": True, "embarque_eliminar": True}
    return render(request, "erp/mantenedores/inventario/embarque_form.html", {
        "form": form, "permisos": permisos,
    })

def embarque_eliminar(request, pk):
    embarque = get_object_or_404(EmbarqueImportacion, pk=pk)
    if request.method == "POST":
        # Verificación simple para no borrar si tiene movimientos
        if embarque.movimientos.exists():
            messages.error(request, "❌ No puedes eliminar un embarque que tiene movimientos de inventario asociados.")
            return redirect("erp_embarques_listar")
        embarque.delete()
        messages.success(request, "✅ Embarque eliminado correctamente.")
        return redirect("erp_embarques_listar")
    permisos = {"embarque_crear": True, "embarque_editar": True, "embarque_eliminar": True}
    return render(request, "erp/mantenedores/inventario/embarque_confirmar_eliminar.html", {
        "embarque": embarque, "permisos": permisos,
    })

def exportar_embarques_excel(request):
    embarques = EmbarqueImportacion.objects.select_related("proveedor").order_by("-fecha_eta")
    wb = Workbook()
    ws = wb.active
    ws.title = "Embarques"
    encabezados = [
        "ID", "Código BL", "Proveedor", "Incoterm", "Estado", 
        "Fecha ETD", "Fecha ETA", "Costo Flete", "Costo Seguro", "Impuestos"
    ]
    ws.append(encabezados)
    for e in embarques:
        ws.append([
            e.id, e.codigo_bl, e.proveedor.razon_social if e.proveedor else "",
            e.incoterm, e.get_estado_display(),
            e.fecha_etd.strftime("%d-%m-%Y") if e.fecha_etd else "",
            e.fecha_eta.strftime("%d-%m-%Y") if e.fecha_eta else "",
            float(e.costo_flete), float(e.costo_seguro), float(e.impuestos_internacion)
        ])
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="embarques_importacion.xlsx"'
    wb.save(response)
    return response
