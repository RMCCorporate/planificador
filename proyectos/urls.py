from django.urls import path
from django.contrib import admin
from proyectos import views

urlpatterns = [
    path('planificador', views.planificador, name='planificador'),
]
