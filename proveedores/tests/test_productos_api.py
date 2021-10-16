from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from planificador.models import Proveedor

from proveedores.api.serializers import ProveedorSerializer


PROVEEDORES_URL = reverse('proveedores:proveedores-list')


class PublicProveedoresApiTests(TestCase):
    """Test thje publicly available PROVEEDOR API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(PROVEEDORES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



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
        Proveedor.objects.create(
            rut="Test rut 1",
            nombre="Test name 1",
            razon_social="Test razón social",
            direccion="Adress Test",
        )
        Proveedor.objects.create(
            rut="Test rut 2",
            nombre="Test name 2",
            razon_social="Test razón social",
            direccion="Adress Test",
        )

        res = self.client.get(PROVEEDORES_URL)

        proveedores = Proveedor.objects.all().order_by('-name')
        serializer = ProveedorSerializer(proveedores, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)