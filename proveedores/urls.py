from django.urls import path
from django.contrib import admin
from proveedores import views

urlpatterns = [
    path('proveedores', views.proveedores, name='proveedores'),
    path('proveedores/nuevo', views.agregar_proveedor, name='nuevo'),
    path('proveedores/agregar_nuevo', views.recibir_datos_proveedor, name='agregar_nuevo'),
    #path('productos/producto/<str:id>', views.producto, name='producto'),
    #path('productos/mostrar_edicion_productos/<str:id>', views.mostrar_edicion_producto, name="mostrar_edicion_producto"),
    #path('productos/eliminar_producto/<str:id>', views.eliminar_producto, name='eliminar_producto'),
]