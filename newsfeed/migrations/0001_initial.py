# Generated by Django 4.2.13 on 2024-09-28 06:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("matchmaking", "0002_initial"),
        ("clubs", "0002_initial"),
        ("tournaments", "0001_initial"),
        ("leagues", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Newsfeed",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NewsfeedPost",
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
                    "post_type",
                    models.CharField(
                        choices=[
                            ("match", "Match Post"),
                            ("league", "League Post"),
                            ("tournament", "Tournament Post"),
                            ("transfer", "Transfer Post"),
                        ],
                        max_length=50,
                    ),
                ),
                ("post_id", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("pinned", models.BooleanField(default=False)),
                ("likes", models.IntegerField(default=0)),
                ("comments", models.JSONField(default=list)),
                ("shares", models.IntegerField(default=0)),
                ("edited_at", models.DateTimeField(blank=True, null=True)),
                (
                    "newsfeed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to="newsfeed.newsfeed",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransferPost",
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
                    "transfer_type",
                    models.CharField(
                        choices=[("join", "Join"), ("quit", "Quit")], max_length=50
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="clubs.club"
                    ),
                ),
                (
                    "newsfeed_post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transfer_post",
                        to="newsfeed.newsfeedpost",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TournamentPost",
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
                ("post_content", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "newsfeed_post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tournament_post",
                        to="newsfeed.newsfeedpost",
                    ),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tournament_posts",
                        to="tournaments.tournament",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MatchPost",
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
                ("post_content", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_posts",
                        to="matchmaking.match",
                    ),
                ),
                (
                    "newsfeed_post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_post",
                        to="newsfeed.newsfeedpost",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeaguePost",
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
                ("post_content", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="league_posts",
                        to="leagues.league",
                    ),
                ),
                (
                    "newsfeed_post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="league_post",
                        to="newsfeed.newsfeedpost",
                    ),
                ),
            ],
        ),
    ]
