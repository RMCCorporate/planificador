# Generated by Django 3.1.7 on 2021-03-31 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0058_cotizacion_proveedor_asociado"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="contacto_asociado",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contacto_asociado",
                to="planificador.contacto",
            ),
        ),
    ]
