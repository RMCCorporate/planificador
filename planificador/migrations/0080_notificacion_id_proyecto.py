# Generated by Django 3.1.7 on 2021-04-23 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0079_remove_notificacion_tipo_notificacion"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacion",
            name="id_proyecto",
            field=models.CharField(max_length=128, null=True),
        ),
    ]
