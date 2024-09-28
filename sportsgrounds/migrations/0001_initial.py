# Generated by Django 4.2.13 on 2024-09-28 06:02

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("matchmaking", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Facilities",
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
                ("facility_name", models.CharField(max_length=255)),
                ("facility_description", models.TextField()),
                (
                    "facility_price",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "photo_url",
                    models.ImageField(
                        blank=True, null=True, upload_to="facilities/photos/"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TimeSlot",
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
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("is_reserved", models.BooleanField(default=False)),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_slots",
                        to="sportsgrounds.facilities",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SportsGround",
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
                ("name", models.CharField(max_length=255)),
                (
                    "profile_photo",
                    models.ImageField(
                        blank=True, null=True, upload_to="sportsgrounds/photos/"
                    ),
                ),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ("description", models.TextField(blank=True, null=True)),
                ("support", models.TextField(blank=True, null=True)),
                ("rules", models.TextField(blank=True, null=True)),
                ("opening_hours", models.JSONField(blank=True, null=True)),
                (
                    "average_rating",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
                ),
                (
                    "followers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="followed_grounds",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_ground",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviews",
                    models.ManyToManyField(
                        blank=True,
                        related_name="ground_reviews",
                        to="matchmaking.groundreview",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="facilities",
            name="sports_ground",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="facilities",
                to="sportsgrounds.sportsground",
            ),
        ),
        migrations.CreateModel(
            name="Booking",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("scheduled", "Scheduled"),
                            ("ongoing", "Ongoing"),
                            ("completed", "Completed"),
                            ("canceled", "Canceled"),
                        ],
                        default="pending",
                        max_length=50,
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="sportsgrounds.facilities",
                    ),
                ),
                (
                    "sports_ground",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="sportsgrounds.sportsground",
                    ),
                ),
                (
                    "time_slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sportsgrounds.timeslot",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
