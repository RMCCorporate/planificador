from django.urls import path
from calculo import views

urlpatterns = [
     path("calculos", views.calculos, name="calculos"),
]
