from django.urls import path
from django.contrib import admin
from proveedores import views

urlpatterns = [
    path('proveedores', views.proveedores, name='proveedores'),
    path('proveedores/nuevo', views.agregar_proveedor, name='nuevo'),
    path('proveedores/agregar_nuevo', views.recibir_datos_proveedor, name='agregar_nuevo'),
    #path('proveedores/proveedor/<str:rut>', views.proveedor, name='proveedor'),
    #path('proveedores/mostrar_edicion_proveedores/<str:rut>', views.mostrar_edicion_proveedor, name="mostrar_edicion_proveedor"),
    #path('proveedores/eliminar_proveedor/<str:rut>', views.eliminar_proveedor, name='eliminar_proveedor'),
]
