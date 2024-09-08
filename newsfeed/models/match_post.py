from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account

from matchmaking.models import Match

class Comment(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    content = models.TextField()

    def __str__(self):
        return f"{self.user} commented on {self.content_object}"


class Like(TimeStampedModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.user} liked {self.content_object}"


class ImageAttachment(models.Model):
    image = models.ImageField(upload_to="custom_post_attachments/images/")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class VideoAttachment(models.Model):
    video = models.FileField(upload_to="custom_post_attachments/videos/")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class TextAttachment(models.Model):
    text = models.TextField(max_length=200)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

class MatchPost(TimeStampedModel):
    """
    Model for a post about a match. It replaces the Club Post
    and Individual Post in the diagram.

    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def __str__(self):
        return f"{self.title} - {self.match}"