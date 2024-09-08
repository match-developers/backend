from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from clubs.models import Club
from matchmaking.choices import MATCH_TYPES, STATUS_CHOICES
from sportsgrounds.models import SportGround


class MatchParticipant(models.Model):
    player = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player} ({self.club})"


class Match(TimeStampedModel):
    sports_ground = models.ForeignKey(SportGround, on_delete=models.CASCADE)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    duration = models.DurationField()
    # is_public is True if the match is open to all users
    # is_public is False if the match is private and only invited users can join
    is_public = models.BooleanField(default=True)
    # is_club is True if the match is between two clubs
    # is_club is False if the match is between several individuals
    is_club = models.BooleanField(default=True)
    total_spots = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    match_type = models.CharField(
        max_length=20, choices=MATCH_TYPES, default="friendly"
    )

    participants = models.ManyToManyField(
        MatchParticipant,
        related_name="matches",
        blank=True,
    )

    @property
    def available_spots(self):
        return self.total_spots - self.participants.count()

    def clean(self):
        if self.is_club and (not self.home or not self.away):
            raise ValidationError(
                "Both home and away clubs are required for club matches."
            )
        if self.is_club and self.match_type not in ["friendly", "tournament", "league"]:
            raise ValidationError("Invalid match type for club matches.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.home} vs {self.away} - {self.match_type} match at {self.sports_ground}"


class MatchScore(TimeStampedModel):
    match = models.OneToOneField(Match, related_name="score", on_delete=models.CASCADE)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            f"{self.match.home} {self.home_score} - {self.away_score} {self.match.away}"
        )


class Goal(TimeStampedModel):
    match = models.ForeignKey(Match, related_name="goals", on_delete=models.CASCADE)
    scorer = models.ForeignKey(MatchParticipant, on_delete=models.CASCADE)
    time_scored = models.DateTimeField()

    def __str__(self):
        return f"{self.scorer} scored at {self.time_scored}"

