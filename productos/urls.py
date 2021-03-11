from django.urls import path
from django.contrib import admin
from productos import views

urlpatterns = [
    path('productos', views.productos, name='productos'),
    path('productos/nuevo', views.agregar_producto, name='nuevo'),
     path('productos/agregar_nuevo', views.recibir_datos_producto, name='agregar_nuevo'),

]