# Generated by Django 3.1.7 on 2021-03-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0050_auto_20210323_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto_proyecto',
            name='status',
            field=models.CharField(choices=[('Urgente', 'Urgente'), ('Transporte', 'Transporte'), ('Bodega', 'Bodega'), ('Futuro', 'Futuro')], default='Futuro', max_length=128),
        ),
    ]
