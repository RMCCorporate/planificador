# Generated by Django 3.1.7 on 2021-07-23 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0107_auto_20210714_1339"),
    ]

    operations = [
        migrations.CreateModel(
            name="Correlativo_orden_compra",
            fields=[
                ("año", models.IntegerField(primary_key=True, serialize=False)),
                ("numero", models.IntegerField()),
            ],
        ),
    ]
