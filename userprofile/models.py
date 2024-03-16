from django.db import models

from matchmaking.models import Match
from newsfeed.models import Post


class IndividualPost(Post):
    scheduled_time = models.DateField()
    match_time = models.DateTimeField(null=True, blank=True)
    score = models.CharField(max_length=50, null=True, blank=True)
    scorer = models.CharField(max_length=255, null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
