from django.core.exceptions import ValidationError
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from clubs.models import Club
from matchmaking.choices import STATUS_CHOICES
from sports.choices import SPORT_CHOICES
from sportsgrounds.models import SportGround


class Match(TimeStampedModel):
    MATCH_TYPES = (
        ("friendly", "Friendly"),
        ("tournament", "Tournament"),
        ("league", "League"),
        ("ranked", "Ranked"),
        ("competitive", "Competitive"),
    )
    sports_ground = models.ForeignKey(SportGround, on_delete=models.CASCADE)
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE)
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
    start_time = models.DateTimeField()
    duration = models.DurationField()
    # is_public is True if the match is open to all users
    # is_public is False if the match is private and only invited users can join
    is_public = models.BooleanField(default=True)
    # is_club is True if the match is between two clubs
    # is_club is False if the match is between several individuals
    is_club = models.BooleanField(default=True)
    available_spots = models.IntegerField()
    total_spots = models.IntegerField()
    average_level = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    match_type = models.CharField(
        max_length=20, choices=MATCH_TYPES, default="friendly"
    )

    def clean(self):
        if self.is_club and (not self.home or not self.away):
            raise ValidationError(
                "Both home and away clubs are required for club matches."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class MatchScore(TimeStampedModel):
    match = models.OneToOneField(Match, related_name="score", on_delete=models.CASCADE)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)


class MatchParticipant(models.Model):
    POSITION_CHOICES = (
        ("GK", "Goalkeeper"),
        ("RB", "Right Back"),
        ("CB", "Center Back"),
        ("LB", "Left Back"),
        ("RM", "Right Midfielder"),
        ("CM", "Center Midfielder"),
        ("LM", "Left Midfielder"),
        ("RW", "Right Winger"),
        ("CF", "Center Forward"),
        ("LW", "Left Winger"),
    )

    player = models.ForeignKey(Account, on_delete=models.CASCADE)
    match = models.ForeignKey(
        Match, related_name="participants", on_delete=models.CASCADE
    )
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)

    class Meta:
        unique_together = ("player", "match")


class Goal(TimeStampedModel):
    match = models.ForeignKey(Match, related_name="goals", on_delete=models.CASCADE)
    scorer = models.ForeignKey(Account, on_delete=models.CASCADE)
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
