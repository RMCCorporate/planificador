# Generated by Django 3.1.7 on 2021-04-30 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0085_auto_20210426_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='filtro_producto',
            name='id_producto',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
