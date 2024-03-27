from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from clubs.models import Club
from matchmaking.models import Match
from newsfeed.models import Comment, Like


class League(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=100)
    clubs = models.ManyToManyField(Club, related_name="leagues")

    def __str__(self):
        return f"{self.name} - {self.season}"


class LeagueRound(models.Model):
    league = models.ForeignKey(League, related_name="rounds", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.league} - {self.name}"


class LeagueMatch(models.Model):
    round = models.ForeignKey(
        LeagueRound, related_name="matches", on_delete=models.CASCADE
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.round} - {self.match}"


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

    def __str__(self):
        return f"{self.club} - {self.league}"


class LeagueTablePost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def __str__(self):
        return f"{self.title} - {self.league}"
