from django.urls import path
from django.contrib import admin
from proyectos import views

urlpatterns = [
    path('planificador', views.planificador, name='planificador'),
    path('lista_productos', views.recibir_datos_planificador, name='lista_productos'),
    path('lista_proveedores', views.recibir_cantidades_planificador, name='lista_proveedores'),
    path('lista_correos', views.enviar_correos, name='lista_correos'),


]
