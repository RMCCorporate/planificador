from django.urls import path
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
        "importaciones/cotizacion_dhl/<str:codigo>",
        views.cotizacion_dhl,
        name="cotizacion_dhl",
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
    path(
        "importaciones/enviar_cotizacion",
        views.enviar_cotización,
        name="enviar_cotizacion",
    ),
    path(
        "importaciones/enviar_correo",
        views.enviar_correo,
        name="enviar_correo",
    ),
]
