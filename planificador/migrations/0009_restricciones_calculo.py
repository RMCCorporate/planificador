# Generated by Django 3.2.6 on 2021-12-17 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0008_auto_20211217_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='restricciones',
            name='calculo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='calculo', to='planificador.calculo'),
        ),
    ]
