# Generated by Django 4.2.3 on 2024-03-20 02:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sportsgrounds", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sportgroundgallery",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
