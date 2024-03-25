from django.db import models

from clubs.models import Club
from matchmaking.models import Match


class Tournament(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Stage(models.Model):
    TOURNAMENT_STAGE_TYPES = (
        ("group", "Group Stage"),
        ("round_of_16", "Round of 16"),
        ("quarter_final", "Quarter-final"),
        ("semi_final", "Semi-final"),
        ("final", "Final"),
        ("other", "Other"),
    )
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
    home = models.ForeignKey(
        Club, related_name="home_tournament_matches", on_delete=models.CASCADE
    )
    away = models.ForeignKey(
        Club, related_name="away_tournament_matches", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.home} vs {self.away}"
