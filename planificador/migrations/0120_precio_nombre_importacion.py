# Generated by Django 3.1.7 on 2021-08-25 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0119_auto_20210823_2117"),
    ]

    operations = [
        migrations.AddField(
            model_name="precio",
            name="nombre_importacion",
            field=models.CharField(max_length=128, null=True),
        ),
    ]
