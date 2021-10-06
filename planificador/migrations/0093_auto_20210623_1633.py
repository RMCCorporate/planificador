# Generated by Django 3.1.7 on 2021-06-23 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planificador", "0092_usuario_nickname"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImagenProducto",
            fields=[
                (
                    "id",
                    models.CharField(max_length=128, primary_key=True, serialize=False),
                ),
                ("imagen", models.ImageField(null=True, upload_to="images")),
            ],
        ),
        migrations.RemoveField(
            model_name="producto",
            name="imagen",
        ),
        migrations.AddField(
            model_name="producto",
            name="imagen",
            field=models.ManyToManyField(to="planificador.ImagenProducto"),
        ),
    ]
