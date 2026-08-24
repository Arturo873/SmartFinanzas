import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SmartFinanzas.settings")
django.setup()

from erp.catalogo.models import Categoria, Producto
from erp.inventario.models import MovimientoInventario
from erp.proveedores.models import ProveedorProducto

MovimientoInventario.objects.all().delete()
ProveedorProducto.objects.all().delete()
Producto.objects.all().delete()
Categoria.objects.all().delete()

print("Catálogo y movimientos limpiados.")
