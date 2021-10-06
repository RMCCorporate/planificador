# Generated by Django 3.1.7 on 2021-06-30 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0097_auto_20210630_1447"),
    ]

    operations = [
        migrations.CreateModel(
            name="Correlativo_orden_compra",
            fields=[
                (
                    "id",
                    models.CharField(max_length=128, primary_key=True, serialize=False),
                ),
                ("numero", models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name="orden_compra",
            name="destino_factura",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="destino_factura",
                to="planificador.rmc",
            ),
        ),
    ]
