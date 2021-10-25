from rest_framework import serializers

from planificador.models import Proveedor, RMC


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer for Proveedor objects"""

    class Meta:
        model = Proveedor
        fields = ('rut', 'nombre', 'razon_social', 'idioma', 'direccion')


class RMCSerializer(serializers.ModelSerializer):
    """Serializer for RMC objects"""

    class Meta:
        model = RMC
        fields = ('rut', 'nombre', 'giro', 'direccion')
