from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        correo = "test@londonappdev.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(correo=correo, password=password)
        self.assertEqual(user.correo, correo)
        self.assertTrue(user.check_password(password))
