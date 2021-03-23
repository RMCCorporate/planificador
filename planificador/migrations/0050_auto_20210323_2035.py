# Generated by Django 3.1.7 on 2021-03-23 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0049_proyecto_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto_proyecto',
            name='proveedores',
            field=models.ManyToManyField(to='planificador.Proveedor'),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='estado',
            field=models.CharField(choices=[('Completo', 'Completo'), ('Incompleto', 'Incompleto')], default='Incompleto', max_length=128, null=True),
        ),
    ]
