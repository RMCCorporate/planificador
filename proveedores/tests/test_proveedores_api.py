from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from planificador.models import Proveedor, Contacto

from proveedores.api.serializers import ProveedorSerializer


PROVEEDORES_URL = reverse('proveedores:proveedores-list')


def sample_proveedor(rut, **params):
    """Create and return a sample proveedor"""
    defaults = {
        'nombre': "Test name 1",
        "razon_social": "Test razón social",
        "direccion": "Adress Test",
    }
    defaults.update(params)

    return Proveedor.objects.create(rut=rut, **defaults)


def sample_contacto(correo, **params):
    """Create a sample contacto"""
    defaults = {
        'telefono': "+56912345678",
        "nombre": "Contacto Test",
    }
    defaults.update(params)

    return Contacto.objects.create(correo=correo, **defaults)


class PublicProveedoresApiTests(TestCase):
    """Test thje publicly available PROVEEDOR API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is not required for retrieving proveedores"""
        res = self.client.get(PROVEEDORES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateProveedoresApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@rmc.cl',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_proveedores(self):
        """Test retrieving tags"""
        sample_proveedor(rut="TestRut1")
        sample_proveedor(rut="TestRut2")

        res = self.client.get(PROVEEDORES_URL)

        proveedores = Proveedor.objects.all().order_by('-nombre')
        serializer = ProveedorSerializer(proveedores, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_proveedor(self):
        """Test creating recipe"""
        payload = {
            'rut': 'sampleRut',
            'nombre': "Test name 1",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
        }
        res = self.client.post(PROVEEDORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        proveedor = Proveedor.objects.get(rut=res.data['rut'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(proveedor, key))

    def test_create_proveedor_with_contactos(self):
        """Test creating proveedor con contactos"""
        contacto1 = sample_contacto(correo="contacto1@gmail.com")
        contacto2 = sample_contacto(correo="contacto2@gmail.com")
        payload = {
            'rut': "Rut prueba",
            'nombre': "Test name 1",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
            'contactos_asociados': [contacto1, contacto2]
        }
        res = self.client.post(PROVEEDORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
