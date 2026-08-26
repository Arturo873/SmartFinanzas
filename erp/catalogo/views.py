from django.shortcuts import render, get_object_or_404, redirect
from erp.catalogo.models import Categoria, Producto
from erp.catalogo.forms import ProductoForm
from django.contrib import messages
from erp.proveedores.models import Proveedor
from erp.inventario.models import MovimientoInventario


def landing(request):
    return render(request, 'erp/catalogo/landing.html')

def catalogo(request):
    categorias = Categoria.objects.all()
    return render(request, 'erp/catalogo/catalogo.html', {
        "categorias": categorias
    })

def subcatalogo(request, categoria):
    categoria_obj = get_object_or_404(Categoria, nombre=categoria)
    productos = Producto.objects.filter(categoria=categoria_obj)
    return render(request, "erp/catalogo/subcatalogo.html", {
        "categoria": categoria_obj,
        "productos": productos
    })

def detalle_producto(request, producto):
    producto_obj = get_object_or_404(Producto, nombre=producto)
    categoria = producto_obj.categoria
    return render(request, "erp/catalogo/detalle.html", {
        "producto": producto_obj.nombre,
        "detalle": producto_obj,
        "categoria": categoria.nombre
    })

def empresa(request):
    data = {
        "historia": "Nstock Importaciones nació con el propósito de conectar mercados internacionales con el comercio local, asegurando abastecimiento constante y variedad.",
        "mision": "Proveer productos de importación de alta rotación y calidad, optimizando la cadena de suministro para nuestros clientes del sector retail.",
        "vision": "Ser el socio logístico y comercial preferido a nivel nacional para la importación directa y distribución de bienes.",
        "valores": ["Transparencia", "Eficiencia Logística", "Calidad Garantizada", "Compromiso Comercial"],
        "contacto": "contacto@nstockimportaciones.com",
        "redes": {
            "Facebook": "https://facebook.com/nstockimportaciones",
            "Instagram": "https://instagram.com/nstockimportaciones"
        }
    }
    return render(request, "erp/catalogo/empresa.html", data)

def mantenedores(request):
    from erp.inventario.models import EmbarqueImportacion
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_movimientos = MovimientoInventario.objects.count()
    total_embarques = EmbarqueImportacion.objects.count()

    return render(request, 'erp/mantenedores/inicioMantenedores.html', {
        "total_productos": total_productos,
        "total_proveedores": total_proveedores,
        "total_usuarios": 0,  # Usuarios removed
        "total_movimientos": total_movimientos,
        "total_embarques": total_embarques,
        "productos_ver": True,
        "proveedores_ver": True,
        "usuarios_ver": False,
        "inventario_ver": True,
        "embarques_ver": True,
    })

def mostrar_todos_productos(request):
    productos = Producto.objects.select_related("categoria").all()
    categorias = Categoria.objects.all()
    return render(request, 'erp/mantenedores/productos/todos_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'productos_crear': True,
        'productos_editar': True,
        'productos_eliminar': True,
    })

def MantenedorAgregarProducto(request):
    form = ProductoForm()
    return render(request, 'erp/mantenedores/productos/MantenedorAgregarProducto.html', {
        "form": form, "productos_crear": True
    })

def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, "✅ Producto creado correctamente.")
            return redirect("erp_mostrar_todos_productos")
        messages.error(request, "❌ Corrige los errores del formulario.")
    else:
        form = ProductoForm()
    return render(request, "erp/mantenedores/productos/MantenedorAgregarProducto.html", {
        "form": form, "productos_crear": True
    })

def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect("erp_mostrar_todos_productos")
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'erp/mantenedores/productos/MantenedorEditarProducto.html', {
        "form": form, "producto": producto, "productos_editar": True
    })

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('erp_mostrar_todos_productos')
    return render(request, 'erp/mantenedores/confirmar_eliminacion.html', {"producto": producto})
