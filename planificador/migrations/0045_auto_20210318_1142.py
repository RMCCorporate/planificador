# Generated by Django 2.1.1 on 2021-03-18 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0044_auto_20210316_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='tipo_cambio',
            field=models.CharField(default='CLP', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='valor_cambio',
            field=models.FloatField(default=1, null=True),
        ),
    ]
