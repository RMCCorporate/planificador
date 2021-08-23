from django.urls import path
from django.contrib import admin
from importaciones import views

urlpatterns = [
    path('importaciones', views.importaciones, name='importaciones'),
    path('importaciones/nueva_importacion_planilla', views.nueva_importacion_planilla, name='nueva_importacion_planilla'),
    path('importaciones/tarifarios', views.tarifarios, name='tarifarios'),
    path('importaciones/tarifarios/tarifario/<str:origin>', views.tarifario, name='tarifario'),
    path('importaciones/nueva_cotizacion_importacion', views.nueva_cotizacion_importacion, name='nueva_cotizacion_importacion'),
]
