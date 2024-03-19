from django.core.exceptions import ValidationError
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from clubs.models import Club
from matchmaking.choices import MATCH_TYPES, STATUS_CHOICES
from sports.choices import SPORT_CHOICES
from sportsgrounds.models import SportGround


class SportPosition(models.Model):
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    position_name = models.CharField(max_length=50)


class MatchParticipant(models.Model):
    player = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)
    position = models.ForeignKey(
        SportPosition, null=True, blank=True, on_delete=models.CASCADE
    )
    is_home_team = models.BooleanField(default=True)


class Match(TimeStampedModel):
    sports_ground = models.ForeignKey(SportGround, on_delete=models.CASCADE)
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
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
    average_level = models.FloatField(default=0.0)
    home = models.ForeignKey(
        Club,
        related_name="home_matches",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    away = models.ForeignKey(
        Club,
        related_name="away_matches",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
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


class MatchScore(TimeStampedModel):
    match = models.OneToOneField(Match, related_name="score", on_delete=models.CASCADE)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)


class Goal(TimeStampedModel):
    match = models.ForeignKey(Match, related_name="goals", on_delete=models.CASCADE)
    scorer = models.ForeignKey(MatchParticipant, on_delete=models.CASCADE)
    time_scored = models.DateTimeField()
    is_penalty = models.BooleanField(default=False)
    is_own_goal = models.BooleanField(default=False)


class FriendlyClubMatch(models.Model):
    home = models.ForeignKey(
        Club, related_name="home_friendly_matches", on_delete=models.CASCADE
    )
    away = models.ForeignKey(
        Club, related_name="away_friendly_matches", on_delete=models.CASCADE
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
