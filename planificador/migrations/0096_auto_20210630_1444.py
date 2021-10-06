# Generated by Django 3.1.7 on 2021-06-30 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0095_orden_compra_rmc"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="orden_compra",
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="productos_proyecto_asociados",
            field=models.ManyToManyField(
                null=True,
                related_name="productos_proyecto_asociados",
                to="planificador.Producto_proyecto",
            ),
        ),
    ]
