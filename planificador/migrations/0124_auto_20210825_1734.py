# Generated by Django 3.1.7 on 2021-08-25 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0123_producto_proyecto_cantidades_producto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto_proyecto_cantidades',
            name='producto_asociado_cantidades',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='producto_asociado_cantidades', to='planificador.producto_proyecto'),
        ),
    ]
