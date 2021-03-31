import django_filters
from planificador.models import Producto, SubClase, Filtro_producto

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
    class Meta:
        model = Filtro_producto
        fields = {"nombre_producto":['contains'],
    "nombre_clase":['contains'],
    "nombre_subclase":['contains'],
    }