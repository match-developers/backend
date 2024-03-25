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
    members = factory.RelatedFactoryList(
        "accounts.tests.factories.AccountFactory",
        factory_related_name="club",
        size=lambda: random.randint(0, AccountFactory._meta.model.objects.count()),
    )

    class Meta:
        model = Club


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
