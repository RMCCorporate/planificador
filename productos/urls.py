from django.urls import path
from django.contrib import admin
from productos import views

urlpatterns = [
    path('productos', views.productos, name='productos'),
    path('productos/nuevo', views.agregar_producto, name='nuevo'),
    path('productos/agregar_nuevo', views.recibir_datos_producto, name='agregar_nuevo'),
    path('productos/producto/<str:id>', views.producto, name='producto'),
    path('productos/mostrar_edicion_productos/<str:id>', views.mostrar_edicion_producto, name="mostrar_edicion_producto"),
    path('productos/eliminar_producto/<str:id>', views.eliminar_producto, name='eliminar_producto'),
]