# Generated by Django 3.1.7 on 2021-04-14 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0064_precio_usuario_modificacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('correo', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=128, null=True)),
                ('apellido', models.CharField(max_length=128, null=True)),
                ('segundo_apellido', models.CharField(max_length=128, null=True)),
                ('celular', models.CharField(max_length=128, null=True)),
                ('cargo', models.CharField(max_length=128, null=True)),
                ('telefono', models.CharField(max_length=128, null=True)),
                ('cotizaciones', models.ManyToManyField(to='planificador.Cotizacion')),
                ('precios', models.ManyToManyField(to='planificador.Precio')),
                ('productos_proyecto', models.ManyToManyField(to='planificador.Producto_proyecto')),
                ('proyectos', models.ManyToManyField(to='planificador.Proyecto')),
            ],
        ),
    ]
