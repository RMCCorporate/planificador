from django.urls import path
from django.contrib import admin
from proyectos import views

urlpatterns = [
    path('planificador', views.planificador, name='planificador'),
    path('mostrar_filtro', views.mostrar_filtro, name='mostrar_filtro'),
    path('guardar_filtro', views.guardar_datos_filtro, name='guardar_filtro'),
    path('lista_productos', views.recibir_datos_planificador, name='lista_productos'),
    path('lista_proveedores', views.recibir_cantidades_planificador, name='lista_proveedores'),
    #path('lista_correos', views.enviar_correos, name='lista_correos'),
    path('proyectos', views.proyectos, name='proyectos'),
    path('proyectos/proyecto/<str:id>', views.proyecto, name='proyecto'),
    path('proyectos/editar_precios/<str:id>', views.editar_precios, name='editar_precios'),
    path('proyectos/editar_producto_proyecto/<str:id>', views.editar_datos_producto_proyecto, name='editar_producto_proyecto'),
    path('proyectos/agregar_producto/<str:id>', views.agregar_producto, name='agregar_producto'),
    path('proyectos/crear_nuevo_producto', views.crear_nuevo_producto, name='crear_nuevo_producto'),
]
