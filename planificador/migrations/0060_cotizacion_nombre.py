# Generated by Django 3.1.7 on 2021-03-31 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0059_cotizacion_contacto_asociado'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizacion',
            name='nombre',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
