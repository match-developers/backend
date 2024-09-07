from django.db import models

from matchmaking.models import Match
from tournaments.choices import TOURNAMENT_STAGE_TYPES

from . import Stage

class TournamentMatch(models.Model):
    stage = models.ForeignKey(Stage, related_name="matches", on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.stage} - {self.match}"
