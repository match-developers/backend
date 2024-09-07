from django.db import models

from matchmaking.models import Match
from tournaments.choices import TOURNAMENT_STAGE_TYPES


class Stage(models.Model):
    tournament = models.ForeignKey(
        Tournament, related_name="stages", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TOURNAMENT_STAGE_TYPES)

    def __str__(self):
        return f"{self.tournament} - {self.name}"


class TournamentMatch(models.Model):
    stage = models.ForeignKey(Stage, related_name="matches", on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.stage} - {self.match}"
