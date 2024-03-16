from django.db import models

from newsfeed.models import Post


class Club(models.Model):
    name = models.CharField(max_length=100)


class ClubPost(Post):
    scheduled_time = models.DateField()
    match_time = models.DateTimeField(null=True, blank=True)
    score = models.CharField(max_length=50, null=True, blank=True)
    scorer = models.CharField(max_length=255, null=True, blank=True)
    match = models.ForeignKey("matchmaking.Match", on_delete=models.CASCADE)


class FriendlyClubMatch(models.Model):
    home = models.ForeignKey(
        Club, related_name="home_friendly_matches", on_delete=models.CASCADE
    )
    away = models.ForeignKey(
        Club, related_name="away_friendly_matches", on_delete=models.CASCADE
    )
    match = models.ForeignKey("matchmaking.Match", on_delete=models.CASCADE)
