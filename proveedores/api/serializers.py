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
        fields = ('nombre', 'descripción')


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer for Proveedor objects"""
    contactos_asociados = ContactoSerializer(many=True, required=False)
    calificaciones = CalificacionSerializer(many=True, required=False)

    class Meta:
        model = Proveedor
        fields = ('rut', 'nombre', 'razon_social', 'idioma', 'direccion', 'contactos_asociados', 'calificaciones')

    def create(self, validated_data):
        if "contactos_asociados" in validated_data.keys():
            contacto = validated_data.pop('contactos_asociados')
        else:
            contacto = False
        if "calificaciones" in validated_data.keys():
            calificaciones = validated_data.pop('calificaciones')
        else:
            calificaciones = False
        instance = self.Meta.model(**validated_data)
        if contacto:
            for contact_data in contacto:
                contacto_qs = Contacto.objects.filter(correo__iexact=contact_data['correo'])

                if contacto_qs.exists():
                    contacto = contacto_qs.first()
                else:
                    contacto = Contacto.objects.create(**contact_data)
                instance.save()
                instance.contactos_asociados.add(contacto)
        if calificaciones:
            for calificacion_data in calificaciones:
                calificacion_qs = Calificacion.objects.filter(nombre__iexact=contact_data['nombre'])

                if calificacion_qs.exists():
                    calificacion = contacto_qs.first()
                else:
                    calificacion = Calificacion.objects.create(**calificacion_data)
                instance.save()
                instance.calificaciones.add(calificacion)
        instance.save()
        return instance


    def update(self, instance, validated_data):
        if validated_data["contactos_asociados"][0]:
            if Contacto.objects.filter(correo=validated_data["contactos_asociados"][0]["correo"]).exists():
                contacto = Contacto.objects.get(correo=validated_data["contactos_asociados"][0]["correo"])
                instance.contactos_asociados.add(contacto)
                instance.save()
            else:
                nuevo_contacto = Contacto(
                    correo=validated_data["contactos_asociados"][0]["correo"],
                    telefono=validated_data["contactos_asociados"][0]["telefono"],
                    nombre=validated_data["contactos_asociados"][0]["nombre"], 
                    )
                nuevo_contacto.save()
                instance.contactos_asociados.add(nuevo_contacto)
                instance.save()
        return instance


class RMCSerializer(serializers.ModelSerializer):
    """Serializer for RMC objects"""

    class Meta:
        model = RMC
        fields = ('rut', 'nombre', 'giro', 'direccion')
