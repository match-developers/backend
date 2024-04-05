from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from newsfeed.models import Comment, Like


class RankPost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)
