from django.db import models
from django.forms import ValidationError

from model_utils.models import TimeStampedModel

from accounts.models import Account
from matchmaking.models import Match


class ClubPost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)


class IndividualPost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)


class Comment(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    club_post = models.ForeignKey(
        ClubPost, on_delete=models.CASCADE, null=True, blank=True
    )
    individual_post = models.ForeignKey(
        IndividualPost, on_delete=models.CASCADE, null=True, blank=True
    )
    content = models.TextField()

    def clean(self):
        if not self.club_post and not self.individual_post:
            raise ValidationError("Either club_post or individual_post is required.")


class Like(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    club_post = models.ForeignKey(
        ClubPost, on_delete=models.CASCADE, null=True, blank=True
    )
    individual_post = models.ForeignKey(
        IndividualPost, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True
    )

    def clean(self):
        if not self.club_post and not self.individual_post and not self.comment:
            raise ValidationError(
                "Either club_post or individual_post or comment is required."
            )
