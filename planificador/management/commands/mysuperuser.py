import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username='tacorrea').exists():
            User.objects.create_superuser('tacorrea',
                                          'tacorrea@uc.cl',
                                          'tom12345')
        if not Group.objects.filter(name='Admin').exists():
            grupo = Group.objects.create('Admin')
            Group.objects.create('Planificador')
            Group.objects.create('Cotizador')
            usuario = User.objects.get(username='tacorrea')
            usuario.groups.add(grupo)
            usuario.save()