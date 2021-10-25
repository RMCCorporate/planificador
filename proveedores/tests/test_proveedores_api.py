from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

import json

from rest_framework import status
from rest_framework.test import APIClient

from planificador.models import Proveedor, Contacto, Calificacion, Producto

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


def sample_calificacion(nombre, **params):
    """Create a sample contacto"""
    defaults = {
        'descripción': "Calificación de prueba",
    }
    defaults.update(params)

    return Calificacion.objects.create(nombre=nombre, **defaults)


def sample_producto(id, **params):
    """Create a sample producto"""
    defaults = {
        'nombre': "Producto prueba",
        'unidad': "Unidad de prueba",
        'kilos': 10,
        'proveedor_interno': "Proveedor de prueba",
    }
    defaults.update(params)

    return Producto.objects.create(id=id, **defaults)


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
        """Test creating proveedor"""
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

    def test_create_proveedor_with_contactos_and_calificaciones(self):
        """Test creating proveedor con contactos and calificaciones"""
        contacto1 = sample_contacto(correo="contacto1@gmail.com")
        contacto2 = sample_contacto(correo="contacto2@gmail.com")
        calificacion1 = sample_calificacion(nombre="Calificacion 1")
        calificacion2 = sample_calificacion(nombre="Calificacion 2")
        payload = {
            'rut': "Rut prueba",
            'nombre': "Test name 1",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
            'contactos_asociados': [contacto1, contacto2],
            'calificaciones': [calificacion1, calificacion2]
        }
        res = self.client.post(PROVEEDORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_proveedor_with_contactos_and_calificaciones_products(self):
        """Test creating proveedor con contactos and calificaciones"""
        contacto1 = sample_contacto(correo="contacto1@gmail.com")
        contacto2 = sample_contacto(correo="contacto2@gmail.com")
        calificacion1 = sample_calificacion(nombre="Calificacion 1")
        calificacion2 = sample_calificacion(nombre="Calificacion 2")
        producto1 = sample_producto(id="1")
        producto2 = sample_producto(id="2")
        payload = {
            'rut': "Rut prueba",
            'nombre': "Test name 1",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
            'contactos_asociados': [contacto1, contacto2],
            'calificaciones': [calificacion1, calificacion2],
            'productos_no': [producto1, producto2]
        }
        res = self.client.post(PROVEEDORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_put_proveedor(self):
        """Test put proveedor"""
        payload = {
            'rut': 'sampleRut',
            'nombre': "Test name 1",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
        }
        res1 = self.client.post(PROVEEDORES_URL, payload)
        payload2 = {
            'rut': 'sampleRut',
            'nombre': "Test name 2",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
        }
        res = self.client.put("{}{}/".format(PROVEEDORES_URL, payload["rut"]), data=json.dumps(payload2), content_type='application/json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_patch_proveedor_with_contacto(self):
        """Test patch proveedor"""
        payload = {
            'rut': 'sampleRut',
            'nombre': "Test name 1",
            "razon_social": "Test razón social",
            "direccion": "Adress Test",
        }
        res1 = self.client.post(PROVEEDORES_URL, payload)
        payload2 = {
            "contactos_asociados":
            [{
                "correo": "sample@sample.cl",
                "nombre": "Contacto Test",
                'telefono': "+56912345678"
            }]
        }
        res = self.client.patch("{}{}/".format(PROVEEDORES_URL, payload["rut"]), data=json.dumps(payload2), content_type='application/json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
