from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account


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


class CustomPost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.title


class ImageAttachment(models.Model):
    image = models.ImageField(upload_to="custom_post_attachments/images/")


class VideoAttachment(models.Model):
    video = models.FileField(upload_to="custom_post_attachments/videos/")


class TextAttachment(models.Model):
    text = models.TextField()
