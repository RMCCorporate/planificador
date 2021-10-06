# Generated by Django 2.1.1 on 2021-03-12 13:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0006_auto_20210312_1344"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producto",
            name="fechas_actualizaciones_historicas",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=128, null=True),
                default=list,
                size=None,
            ),
        ),
    ]
