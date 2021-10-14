from django.test import TestCase


class CalcTests(TestCase):

    def test_add_numbers(self):
        self.assertEqual((3+8), 11)