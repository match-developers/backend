# Generated by Django 4.2.3 on 2024-03-20 01:49

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SportGround",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ("description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="SportGroundGallery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("image", models.ImageField(upload_to="sportsgrounds/gallery/")),
                ("description", models.TextField()),
                (
                    "sportground",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery",
                        to="sportsgrounds.sportground",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
