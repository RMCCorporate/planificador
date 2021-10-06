from django.urls import path
from django.contrib import admin
from importaciones import views

urlpatterns = [
    path(
        "importaciones/guardar_filtro",
        views.guardar_datos_filtro,
        name="guardar_filtro",
    ),
    path(
        "importaciones/lista_productos",
        views.recibir_datos_planificador,
        name="lista_productos",
    ),
    path("importaciones", views.importaciones, name="importaciones"),
    path(
        "importaciones/anadir_importacion",
        views.anadir_importacion,
        name="anadir_importacion",
    ),
    path(
        "importaciones/importacion/<str:importacion>",
        views.importacion,
        name="importacion",
    ),
    path(
        "importaciones/nueva_importacion_planilla",
        views.nueva_importacion_planilla,
        name="nueva_importacion_planilla",
    ),
    path("importaciones/tarifarios", views.tarifarios, name="tarifarios"),
    path(
        "importaciones/tarifarios/tarifario/<str:origin>",
        views.tarifario,
        name="tarifario",
    ),
    path(
        "importaciones/nueva_cotizacion_importacion",
        views.nueva_cotizacion_importacion,
        name="nueva_cotizacion_importacion",
    ),
]
