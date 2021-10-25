from rest_framework import serializers

from planificador.models import Proveedor, RMC, Contacto, Calificacion


class ContactoSerializer(serializers.ModelSerializer):
    """Serializer for Contacto objects"""

    class Meta:
        model = Contacto
        fields = ('correo', 'telefono', 'nombre')


class CalificacionSerializer(serializers.ModelSerializer):
    """Serializer for Contacto objects"""

    class Meta:
        model = Calificacion
        fields = ('nombre', 'descripcion')


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer for Proveedor objects"""
    contactos_asociados = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Contacto.objects.all() 
    )
    calificaciones = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Calificacion.objects.all() 
    )

    class Meta:
        model = Proveedor
        fields = ('rut', 'nombre', 'razon_social', 'idioma', 'direccion', 'contactos_asociados', 'calificaciones')

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
    
    def put(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def patch(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

class RMCSerializer(serializers.ModelSerializer):
    """Serializer for RMC objects"""

    class Meta:
        model = RMC
        fields = ('rut', 'nombre', 'giro', 'direccion')
