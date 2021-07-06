from django.urls import path
from django.contrib import admin
from proyectos import views
from orden_compra import views as orden_compra_views

urlpatterns = [
    path('planificador', views.planificador, name='planificador'),
    path('mostrar_filtro', views.mostrar_filtro, name='mostrar_filtro'),
    path('guardar_filtro', views.guardar_datos_filtro, name='guardar_filtro'),
    path('lista_productos', views.recibir_datos_planificador, name='lista_productos'),
    path('lista_proveedores', views.recibir_cantidades_planificador, name='lista_proveedores'),
    path('proyectos', views.proyectos, name='proyectos'),
    path('proyectos/proyecto/<str:id>', views.proyecto, name='proyecto'),
    path('proyectos/editar_precios/<str:id>', views.editar_precios, name='editar_precios'),
    path('editar_fechas/<str:id>', views.editar_fechas, name='editar_fechas'),
    path('proyectos/editar_producto_proyecto/<str:id>', views.editar_datos_producto_proyecto, name='editar_producto_proyecto'),
    path('proyectos/agregar_cotizacion/<str:id>', views.agregar_cotizacion, name='agregar_cotizacion'),
    path('agregar_producto/<str:id>', views.agregar_producto, name='agregar_producto'),
    path('proyectos/crear_nuevo_producto', views.crear_nuevo_producto, name='crear_nuevo_producto'),
    path('proyectos/informar_orden_compra/<str:id>', views.informar_orden_compra, name='informar_orden_compra'),
    path('proyectos/mostrar_cotizacion/<str:id>', views.mostrar_cotizacion, name='mostrar_cotizacion'),
    path('proyectos/editar_cotizacion/<str:id>', views.editar_cotizacion, name='editar_cotizacion'),
    path('proyectos/eliminar_cotizacion/<str:id>', views.eliminar_cotizacion, name='eliminar_cotizacion'),
    path('proyectos/enviar_correo/<str:id>', views.enviar_correo, name='enviar_correo'),
    path('orden_compra/crear_orden/<str:id>', orden_compra_views.crear_orden, name='crear_orden'),
]
