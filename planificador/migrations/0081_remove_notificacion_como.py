# Generated by Django 3.1.7 on 2021-04-23 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0080_notificacion_id_proyecto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificacion',
            name='como',
        ),
    ]
