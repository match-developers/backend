from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account


class Club(TimeStampedModel):
    name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="clubs/profile_pictures/")
    owner = models.ForeignKey(
        Account, related_name="clubs_owned", on_delete=models.CASCADE
    )
    foundation_date = models.DateField(null=True, blank=True)
    members = models.ManyToManyField(
        Account, related_name="club_memberships", blank=True
    )

    def __str__(self):
        return self.name
