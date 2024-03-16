# Generated by Django 4.2.3 on 2024-03-16 01:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("clubs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="League",
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
                ("season", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="LeagueRound",
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
                (
                    "league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rounds",
                        to="leagues.league",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeaguePosition",
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
                ("position", models.IntegerField()),
                ("points", models.IntegerField()),
                ("played", models.IntegerField()),
                ("won", models.IntegerField()),
                ("drawn", models.IntegerField()),
                ("lost", models.IntegerField()),
                ("goals_for", models.IntegerField()),
                ("goals_against", models.IntegerField()),
                ("goal_difference", models.IntegerField()),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="league_positions",
                        to="clubs.club",
                    ),
                ),
                (
                    "league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="leagues.league",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeagueMatch",
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
                    "away",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="away_league_matches",
                        to="clubs.club",
                    ),
                ),
                (
                    "home",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="home_league_matches",
                        to="clubs.club",
                    ),
                ),
            ],
        ),
    ]
