from django.urls import path, include

from proveedores import views
from proveedores.api.router import router_proveedores

#app_name = 'proveedores'

urlpatterns = [
    path('', include(router_proveedores.urls)),
    path("proveedores", views.proveedores, name="proveedores"),
    path("proveedores/nuevo", views.agregar_proveedor, name="nuevo"),
    path(
        "proveedores/agregar_nuevo", views.recibir_datos_proveedor, name="agregar_nuevo"
    ),
    path("proveedores/proveedor/<str:rut>", views.proveedor, name="proveedor"),
    path(
        "productos/nuevo_proveedor_planilla",
        views.nuevo_proveedor_planilla,
        name="nuevo_proveedor_planilla",
    ),
    path(
        "proveedores/mostrar_edicion_proveedores/<str:rut>",
        views.mostrar_edicion_proveedor,
        name="mostrar_edicion_proveedor",
    ),
    path(
        "proveedores/agregar_productos_no_disponibles/<str:rut>",
        views.agregar_productos_no_disponibles,
        name="agregar_productos_no_disponibles",
    ),
    path(
        "proveedores/eliminar_proveedor/<str:rut>",
        views.eliminar_proveedor,
        name="eliminar_proveedor",
    ),
]
