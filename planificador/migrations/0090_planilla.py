# Generated by Django 3.1.7 on 2021-06-22 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0089_correlativo_producto"),
    ]

    operations = [
        migrations.CreateModel(
            name="Planilla",
            fields=[
                (
                    "id",
                    models.CharField(max_length=128, primary_key=True, serialize=False),
                ),
                ("planilla", models.FileField(upload_to="img")),
            ],
        ),
    ]
