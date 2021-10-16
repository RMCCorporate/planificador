from django.test import TestCase
from django.contrib.auth import get_user_model

from planificador import models


def sample_user(correo='test@rmc.cl', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(correo, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        correo = "test@rmc.cl"
        password = "Testpass123"
        user = get_user_model().objects.create_user(correo=correo, password=password)
        self.assertEqual(user.correo, correo)
        self.assertTrue(user.check_password(password))

    def test_proveedor_str(self):
        """Test the proveedor string representation"""
        proveedor = models.Proveedor.objects.create(
            rut="Test rut",
            nombre="Test name",
            razon_social="Test razón social",
            direccion="Adress Test",
        )

        self.assertEqual(str(proveedor), proveedor.nombre)
