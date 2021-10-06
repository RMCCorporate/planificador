from django.urls import path
from django.contrib import admin
from productos import views

urlpatterns = [
    path("productos", views.productos, name="productos"),
    path("productos/nuevo", views.agregar_producto, name="nuevo_producto"),
    path("productos/agregar_nuevo", views.recibir_datos_producto, name="agregar_nuevo"),
    path(
        "productos/nuevo_producto_planilla",
        views.nuevo_producto_planilla,
        name="nuevo_producto_planilla",
    ),
    path(
        "productos/nuevo_producto_interno_planilla",
        views.nuevo_producto_interno_planilla,
        name="nuevo_producto_interno_planilla",
    ),
    path(
        "productos/nuevo_proveedor_producto",
        views.nuevo_proveedor_producto,
        name="nuevo_proveedor_producto",
    ),
    path("productos/producto/<str:id>", views.producto, name="producto"),
    path(
        "productos/mostrar_edicion_productos/<str:id>",
        views.mostrar_edicion_producto,
        name="mostrar_edicion_producto",
    ),
    path(
        "productos/eliminar_producto/<str:id>",
        views.eliminar_producto,
        name="eliminar_producto",
    ),
    path(
        "productos/mostrar_ubicaciones",
        views.mostrar_ubicaciones,
        name="mostrar_ubicaciones",
    ),
]
