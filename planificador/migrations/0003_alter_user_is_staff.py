# Generated by Django 3.2.6 on 2021-10-14 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planificador', '0002_auto_20211014_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=True),
        ),
    ]
