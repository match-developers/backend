from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    content = models.TextField()


class Like(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
