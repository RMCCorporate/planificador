from django.urls import path
from django.contrib import admin
from importaciones import views

urlpatterns = [
    path('importaciones', views.importaciones, name='importaciones'),
    path('importaciones/nueva_importacion_planilla', views.nueva_importacion_planilla, name='nueva_importacion_planilla'),
]
