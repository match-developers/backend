import random

import factory
import factory.fuzzy

from accounts.tests.factories import AccountFactory
from clubs.models import (
    Club,
    ClubGallery,
    ClubNewMemberPost,
    ClubQuitPost,
    ClubTransferDonePost,
    ClubTransferInterestPost,
    ClubTransferInvitePost,
)


class ClubFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    user_name = factory.Faker("user_name")
    description = factory.Faker("text")
    profile_picture = factory.django.ImageField(color="blue")
    owner = factory.SubFactory("accounts.tests.factories.AccountFactory")
    foundation_date = factory.Faker("date")

    class Meta:
        model = Club

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.members.add(member)
        else:
            for _ in range(random.randint(0, 10)):
                member = AccountFactory()
                self.members.add(member)


class ClubGalleryFactory(factory.django.DjangoModelFactory):
    image = factory.django.ImageField(color="blue")
    description = factory.Faker("text")
    club = factory.SubFactory(ClubFactory)

    class Meta:
        model = ClubGallery


class ClubNewMemberPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    new_club = factory.SubFactory(ClubFactory)
    joining_message = factory.Faker("text")

    comments = factory.RelatedFactory(
        "newsfeed.tests.factories.CommentFactory", "content_object"
    )
    likes = factory.RelatedFactory(
        "newsfeed.tests.factories.LikeFactory", "content_object"
    )

    class Meta:
        model = ClubNewMemberPost


class ClubTransferInvitePostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user_invited = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory(ClubFactory)

    comments = factory.RelatedFactory(
        "newsfeed.tests.factories.CommentFactory", "content_object"
    )
    likes = factory.RelatedFactory(
        "newsfeed.tests.factories.LikeFactory", "content_object"
    )

    class Meta:
        model = ClubTransferInvitePost


class ClubTransferDonePostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    previous_club = factory.SubFactory(ClubFactory)
    new_club = factory.SubFactory(ClubFactory)

    comments = factory.RelatedFactory(
        "newsfeed.tests.factories.CommentFactory", "content_object"
    )
    likes = factory.RelatedFactory(
        "newsfeed.tests.factories.LikeFactory", "content_object"
    )

    class Meta:
        model = ClubTransferDonePost


class ClubQuitPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory(ClubFactory)
    quiting_message = factory.Faker("text")

    comments = factory.RelatedFactory(
        "newsfeed.tests.factories.CommentFactory", "content_object"
    )
    likes = factory.RelatedFactory(
        "newsfeed.tests.factories.LikeFactory", "content_object"
    )

    class Meta:
        model = ClubQuitPost


class ClubTransferInterestPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory(ClubFactory)
    joining_message = factory.Faker("text")

    comments = factory.RelatedFactory(
        "newsfeed.tests.factories.CommentFactory", "content_object"
    )
    likes = factory.RelatedFactory(
        "newsfeed.tests.factories.LikeFactory", "content_object"
    )

    class Meta:
        model = ClubTransferInterestPost
