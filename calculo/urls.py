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
     path("calculos/recibir_controles", views.recibir_controles, name="recibir_controles"),
     path("calculos/eleccion_productos_calculos", views.eleccion_productos_calculos, name="eleccion_productos_calculos"),
     path("mostrar_atributos", views.mostrar_atributos, name="mostrar_atributos"),
     path("atributo/<str:nombre>", views.atributo, name="atributo"),
     path(
        "mostrar_edicion_atributo/<str:nombre>",
        views.mostrar_edicion_atributo,
        name="mostrar_edicion_atributo",
    ),
    path(
        "eliminar_atributo/<str:nombre>",
        views.eliminar_atributo,
        name="eliminar_atributo",
    ),
    path("mostrar_calculos", views.mostrar_calculos, name="mostrar_calculos"),
     path("mostrar_calculo/<str:nombre>", views.mostrar_calculo, name="mostrar_calculo"),
     path("mostrar_instalacion_proyecto/<str:nombre>", views.mostrar_instalacion_proyecto, name="mostrar_instalacion_proyecto"),
     path("eliminar_instalacion_proyecto/<str:nombre>", views.eliminar_instalacion_proyecto, name="eliminar_instalacion_proyecto"),
     path(
        "mostrar_edicion_calculo/<str:nombre>",
        views.mostrar_edicion_calculo,
        name="mostrar_edicion_calculo",
    ),
    path(
        "eliminar_calculo/<str:nombre>",
        views.eliminar_calculo,
        name="eliminar_calculo",
    ),
    path("mostrar_restricciones", views.mostrar_restricciones, name="mostrar_restricciones"),
    path("restriccion/<str:nombre>", views.restriccion, name="restriccion"),
    path(
        "mostrar_edicion_restriccion/<str:nombre>",
        views.mostrar_edicion_restriccion,
        name="mostrar_edicion_restriccion",
    ),
    path(
        "eliminar_restriccion/<str:nombre>",
        views.eliminar_restriccion,
        name="eliminar_restriccion",
    ),
    path(
        "mostrar_controles_riesgo",
        views.mostrar_controles_riesgo,
        name="mostrar_controles_riesgo",
    ),
    path("control_riesgo/<str:nombre>", views.control_riesgo, name="control_riesgo"),
    path(
        "editar_control_riesgo/<str:nombre>",
        views.editar_control_riesgo,
        name="editar_control_riesgo",
    ),
    path(
        "eliminar_control_riesgo/<str:nombre>",
        views.eliminar_control_riesgo,
        name="eliminar_control_riesgo",
    ),
    path("calculos/editar_calculo_control_riesgo/<str:nombre>", views.editar_calculo_control_riesgo, name="editar_calculo_control_riesgo"),
    path("calculos/editar_calculo_control_riesgo/guardar_restricciones_control_riesgo/<str:nombre>", views.guardar_restricciones_control_riesgo, name="guardar_restricciones_control_riesgo"),
    path(
        "mostrar_instalaciones",
        views.mostrar_instalaciones,
        name="mostrar_instalaciones",
    ),
    path("instalacion/<str:nombre>", views.instalacion, name="instalacion"),
    path(
        "eliminar_instalacion/<str:nombre>",
        views.eliminar_instalacion,
        name="eliminar_instalacion",
    ),
    path(
        "agregar_control_riesgo_instalacion/<str:nombre>",
        views.agregar_control_riesgo_instalacion,
        name="agregar_control_riesgo_instalacion",
    ),
    path(
        "eliminar_control_riesgo_instalacion/<str:nombre>",
        views.eliminar_control_riesgo_instalacion,
        name="eliminar_control_riesgo_instalacion",
    ),
]

