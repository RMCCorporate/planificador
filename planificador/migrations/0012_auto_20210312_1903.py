# Generated by Django 2.1.1 on 2021-03-12 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0011_auto_20210312_1901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacto',
            name='correo_id',
            field=models.CharField(default='tcorrea@rmc.cl', max_length=254, primary_key=True, serialize=False),
        ),
    ]
