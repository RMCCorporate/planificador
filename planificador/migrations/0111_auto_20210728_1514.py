# Generated by Django 3.1.7 on 2021-07-28 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0110_proyecto_consolidacion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proyecto",
            name="consolidacion",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
