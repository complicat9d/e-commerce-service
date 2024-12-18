# Generated by Django 5.1.4 on 2024-12-05 13:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255, null=True)),
                ("username", models.CharField(max_length=255, null=True)),
                ("lang", models.CharField(default="en", max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("photo", models.CharField(max_length=255, null=True)),
                ("description", models.TextField()),
                ("cost", models.FloatField()),
                ("amount", models.IntegerField(default=0)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="admin_panel.category",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("product_name", models.CharField(max_length=255)),
                ("amount", models.IntegerField()),
                ("cost", models.FloatField()),
                ("address", models.CharField(max_length=255, null=True)),
                ("is_being_delivered", models.BooleanField(default=False)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="admin_panel.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="admin_panel.user",
                    ),
                ),
            ],
        ),
    ]
