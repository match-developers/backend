from django.db import models

from matchmaking.models import Match
from tournaments.choices import TOURNAMENT_STAGE_TYPES


class Tournament(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Stage(models.Model):
    tournament = models.ForeignKey(
        Tournament, related_name="stages", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TOURNAMENT_STAGE_TYPES)

    def __str__(self):
        return f"{self.tournament} - {self.name}"