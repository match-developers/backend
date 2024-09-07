from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from clubs.models import Club
from matchmaking.models import Match
from newsfeed.models import Comment, Like

from . import LeagueRound

class LeagueMatch(models.Model):
    round = models.ForeignKey(
        LeagueRound, related_name="matches", on_delete=models.CASCADE
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.round} - {self.match}"