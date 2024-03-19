from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from newsfeed.models import Comment, Like


class Club(models.Model):
    name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)


class ClubGallery(TimeStampedModel):
    image = models.ImageField(upload_to="clubs/gallery/")
    description = models.TextField()
    club = models.ForeignKey(Club, related_name="gallery", on_delete=models.CASCADE)


class ClubTransferInvitePost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)
