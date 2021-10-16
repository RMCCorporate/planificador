from rest_framework import serializers

from planificador.models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer for Proveedor objects"""

    class Meta:
        model = Proveedor
        fields = ('rut', 'nombre', 'razon_social', 'idioma', 'direccion')
        read_only_fields = ('subclases_asociadas', 'calificaciones')