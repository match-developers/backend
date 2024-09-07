from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from clubs.models import Club
from matchmaking.choices import MATCH_TYPES, STATUS_CHOICES
from newsfeed.models import Comment, Like
from sportsgrounds.models import SportGround


class MatchParticipant(models.Model):
    player = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)
    is_home_team = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.player} ({self.club})"