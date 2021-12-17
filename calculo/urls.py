from django.urls import path
from calculo import views

urlpatterns = [
     path("calculos", views.calculos, name="calculos"),
     path("calculos/crear_atributo", views.crear_atributo, name="crear_atributo"),
     path("calculos/crear_calculos", views.crear_calculo, name="crear_calculo"),
     path("calculos/mostrar_filtro", views.mostrar_filtro_calculo, name="mostrar_filtro"),
     path("calculos/guardar_filtro", views.guardar_datos_filtro, name="guardar_filtro"),
     path("calculos/lista_productos", views.lista_productos, name="lista_productos"),
     path("calculos/crear_control_riesgo", views.crear_control_riesgo, name="crear_control_riesgo"),
     path("calculos/guardar_control_riesgo", views.guardar_control_riesgo, name="guardar_contro_riesgo"),
     path("calculos/crear_instalacion", views.crear_instalacion, name="crear_instalacion"),
     path("calculos/crear_instalacion_proyecto", views.crear_instalacion_proyecto, name="crear_instalacion_proyecto"),
     path("calculos/eleccion_control", views.eleccion_control, name="eleccion_control"),
]

