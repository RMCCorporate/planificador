import django_filters
from django import forms
from planificador.models import (
    Producto,
    SubClase,
    Filtro_producto,
    Clase,
    Proveedor,
    Proyecto,
)


class ProductoFilter(django_filters.FilterSet):
    class Meta:
        model = Producto
        fields = {
            "id": ["contains"],
            "nombre": ["contains"],
        }


class SubclaseFilter(django_filters.FilterSet):
    class Meta:
        model = SubClase
        fields = {
            "nombre": ["contains"],
        }


class Filtro_productoFilter(django_filters.FilterSet):
    nombre_clase = django_filters.ModelMultipleChoiceFilter(
        queryset=Clase.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    nombre_subclase = django_filters.ModelMultipleChoiceFilter(
        queryset=SubClase.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    nombre_producto = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "busquedaproducto"}),
    )

    class Meta:
        model = Filtro_producto
        fields = ["nombre_producto", "nombre_clase", "nombre_subclase"]


class ProveedoresFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "busquedaproducto"}),
    )
    rut = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "busquedaproducto"}),
    )

    class Meta:
        model = Proveedor
        fields = ["rut", "nombre"]


class ProyectosFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "busquedaproducto"}),
    )
    id = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "busquedaproducto"}),
    )

    class Meta:
        model = Proyecto
        fields = ["id", "nombre"]
