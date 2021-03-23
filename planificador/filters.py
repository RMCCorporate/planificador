import django_filters
from planificador.models import Producto

class ProductoFilter(django_filters.FilterSet):
    class Meta:
        model = Producto
        fields = {"id":['contains'],
                 "nombre":['contains'],
                "unidad":['contains'],
               }
               

