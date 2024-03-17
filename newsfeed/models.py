from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from matchmaking.models import Match


class Post(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)


class Comment(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()


class Like(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True
    )


class ClubPost(Post):
    match_time = models.DateTimeField(null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)


class IndividualPost(Post):
    match_time = models.DateTimeField(null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
