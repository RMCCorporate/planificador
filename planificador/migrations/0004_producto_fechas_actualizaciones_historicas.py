# Generated by Django 2.1.1 on 2021-03-12 12:52

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0003_producto_ultimo_proveedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='fechas_actualizaciones_historicas',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), null=True, size=None),
        ),
    ]
