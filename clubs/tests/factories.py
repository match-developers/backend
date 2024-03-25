import factory
import factory.fuzzy

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
    members = factory.RelatedFactory("accounts.tests.factories.AccountFactory")

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

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = ClubNewMemberPost


class ClubTransferInvitePostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user_invited = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory(ClubFactory)

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = ClubTransferInvitePost


class ClubTransferDonePostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    previous_club = factory.SubFactory(ClubFactory)
    new_club = factory.SubFactory(ClubFactory)

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = ClubTransferDonePost


class ClubQuitPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory(ClubFactory)
    quiting_message = factory.Faker("text")

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = ClubQuitPost


class ClubTransferInterestPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory(ClubFactory)
    joining_message = factory.Faker("text")

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = ClubTransferInterestPost
