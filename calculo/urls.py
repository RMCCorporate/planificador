from django.urls import path
from calculo import views

urlpatterns = [
     path("calculos", views.calculos, name="calculos"),
     path("calculos/crear_atributo", views.crear_atributo, name="crear_atributo"),
]
