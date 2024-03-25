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

    def __str__(self):
        return self.name


class ClubGallery(TimeStampedModel):
    image = models.ImageField(upload_to="clubs/gallery/")
    description = models.TextField(blank=True, null=True)
    club = models.ForeignKey(Club, related_name="gallery", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.club} gallery"


class ClubTransferInvitePost(TimeStampedModel):
    """
    Club owner invites a user to join the club.

    """

    title = models.CharField(max_length=255)
    user_invited = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def save(self, *args, **kwargs):
        if self.user_invited in self.club.members.all():
            raise ValueError("User is already a member of the club")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_invited} invited to {self.club}"


class ClubTransferDonePost(TimeStampedModel):
    """
    User has moved to a new club.

    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    previous_club = models.ForeignKey(
        Club, related_name="transfers_from_club_done", on_delete=models.CASCADE
    )
    new_club = models.ForeignKey(
        Club, related_name="transfers_to_club_done", on_delete=models.CASCADE
    )

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def __str__(self):
        return f"{self.user} moved from {self.previous_club} to {self.new_club}"


class ClubTransferInterestPost(TimeStampedModel):
    """
    User is interested in moving to a new club.
    The post can be sent to the club owner or
    can be sent to club community.

    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    joining_message = models.TextField(blank=True, null=True)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def __str__(self):
        return f"{self.user} is interested in {self.club}"


class ClubQuitPost(TimeStampedModel):
    """
    User has quit the club.

    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    quiting_message = models.TextField(blank=True, null=True)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def __str__(self):
        return f"{self.user} quit the {self.club}"


class ClubNewMemberPost(TimeStampedModel):
    """
    User without club has joined to the club.

    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    new_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    joining_message = models.TextField(blank=True, null=True)

    comments = GenericRelation(Comment)
    likes = GenericRelation(Like)

    def __str__(self):
        return f"{self.user} joined to {self.new_club}"
