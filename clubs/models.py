from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel

from accounts.models import Account
from newsfeed.models import Comment, Like


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


class ClubGallery(TimeStampedModel):
    image = models.ImageField(upload_to="clubs/gallery/")
    description = models.TextField(blank=True, null=True)
    club = models.ForeignKey(Club, related_name="gallery", on_delete=models.CASCADE)


class ClubTransferInvitePost(TimeStampedModel):
    title = models.CharField(max_length=255)
    user_invited = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def save(self, *args, **kwargs):
        if self.user_invited in self.club.members.all():
            raise ValueError("User is already a member of the club")
        super().save(*args, **kwargs)
