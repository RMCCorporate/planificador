import django_filters
from django import forms
from planificador.models import Producto, SubClase, Filtro_producto, Clase

class ProductoFilter(django_filters.FilterSet):
    class Meta:
        model = Producto
        fields = {"id":['contains'],
                 "nombre":['contains'],
               }
               
class SubclaseFilter(django_filters.FilterSet):
    class Meta:
        model = SubClase
        fields = {"nombre":['contains'],
        }

class Filtro_productoFilter(django_filters.FilterSet):
    nombre_subclase = django_filters.ModelMultipleChoiceFilter(queryset=SubClase.objects.all(), widget=forms.CheckboxSelectMultiple)
    nombre_clase = django_filters.ModelMultipleChoiceFilter(queryset=Clase.objects.all(), widget=forms.CheckboxSelectMultiple)
    nombre_producto = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'busqueda_producto'}))
    class Meta:
        model = Filtro_producto
        fields = ['nombre_producto','nombre_clase','nombre_subclase']

