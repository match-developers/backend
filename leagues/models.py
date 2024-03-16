from django.db import models

from clubs.models import Club
from matchmaking.models import Match


class League(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=100)


class LeagueRound(models.Model):
    league = models.ForeignKey(League, related_name="rounds", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class LeagueMatch(models.Model):
    round = models.ForeignKey(
        LeagueRound, related_name="matches", on_delete=models.CASCADE
    )
    home = models.ForeignKey(
        Club, related_name="home_league_matches", on_delete=models.CASCADE
    )
    away = models.ForeignKey(
        Club, related_name="away_league_matches", on_delete=models.CASCADE
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)


class LeaguePosition(models.Model):
    league = models.ForeignKey(
        League, related_name="positions", on_delete=models.CASCADE
    )
    club = models.ForeignKey(
        Club, related_name="league_positions", on_delete=models.CASCADE
    )
    position = models.IntegerField()
    points = models.IntegerField()
    played = models.IntegerField()
    won = models.IntegerField()
    drawn = models.IntegerField()
    lost = models.IntegerField()
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()
    goal_difference = models.IntegerField()

    class Meta:
        unique_together = ("league", "club")
