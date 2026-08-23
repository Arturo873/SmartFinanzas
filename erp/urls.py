from django.urls import path
from erp.catalogo import views as catalogo_views
from erp.inventario import views as inventario_views
from erp.proveedores import views as proveedores_views

urlpatterns = [
    # --- Catalogo y Mantenedores (Base) ---
    path('', catalogo_views.landing, name='erp_landing'),
    path('catalogo/', catalogo_views.catalogo, name='erp_catalogo'),
    path('catalogo/<str:categoria>/', catalogo_views.subcatalogo, name='erp_subcatalogo'),
    path('producto/<str:producto>/', catalogo_views.detalle_producto, name='erp_detalle_producto'),
    path('empresa/', catalogo_views.empresa, name='erp_empresa'),
    path('mantenedores/', catalogo_views.mantenedores, name='erp_mantenedores'),

    # --- Productos ---
    path('mantenedores/productos/', catalogo_views.mostrar_todos_productos, name='erp_mostrar_todos_productos'),
    path('mantenedores/productos/agregar/', catalogo_views.crear_producto, name='erp_crear_producto'),
    path('mantenedores/productos/editar/<int:id>/', catalogo_views.editar_producto, name='erp_editar_producto'),
    path('mantenedores/productos/eliminar/<int:id>/', catalogo_views.eliminar_producto, name='erp_eliminar_producto'),

    # --- Inventario ---
    path("mantenedores/inventario/", inventario_views.movimientos_listar, name="erp_movimientos_listar"),
    path("mantenedores/inventario/nuevo/", inventario_views.movimiento_crear, name="erp_movimiento_crear"),
    path("mantenedores/inventario/<int:pk>/editar/", inventario_views.movimiento_editar, name="erp_movimiento_editar"),
    path("mantenedores/inventario/<int:pk>/eliminar/", inventario_views.movimiento_eliminar, name="erp_movimiento_eliminar"),
    path("mantenedores/inventario/exportar/", inventario_views.exportar_movimientos_excel, name="erp_movimientos_exportar"),

    # --- Proveedores ---
    path('mantenedores/proveedores/', proveedores_views.mostrar_todos_proveedores, name='erp_proveedores_listar'),
    path('mantenedores/proveedores/crear/', proveedores_views.crear_proveedor, name='erp_crear_proveedor'),
    path('mantenedores/proveedores/editar/<int:id>/', proveedores_views.editar_proveedor, name='erp_editar_proveedor'),
    path('mantenedores/proveedores/eliminar/<int:id>/', proveedores_views.eliminar_proveedor, name='erp_eliminar_proveedor'),
    path('mantenedores/proveedores/exportar/', proveedores_views.exportar_proveedores_excel, name='erp_exportar_proveedores_excel'),
    path('mantenedores/proveedores/divisiones/<int:pais_id>/', proveedores_views.obtener_divisiones, name='erp_obtener_divisiones'),
]
