# Generated by Django 5.1.4 on 2024-12-05 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_panel", "0003_rename_first_name_faq_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="photo/"),
        ),
    ]
