import factory
import factory.fuzzy

from newsfeed.models import (
    Comment,
    CustomPost,
    ImageAttachment,
    Like,
    TextAttachment,
    VideoAttachment,
)


class CustomPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")

    comments = factory.RelatedFactory(
        "newsfeed.tests.factories.CommentFactory", "content_object"
    )
    likes = factory.RelatedFactory(
        "newsfeed.tests.factories.LikeFactory", "content_object"
    )

    class Meta:
        model = CustomPost


class LikeFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")

    class Meta:
        model = Like


class CommentFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    content = factory.Faker("text")

    class Meta:
        model = Comment


class ImageAttachmentFactory(factory.django.DjangoModelFactory):
    image = factory.django.ImageField()

    class Meta:
        model = ImageAttachment


class VideoAttachmentFactory(factory.django.DjangoModelFactory):
    video = factory.django.FileField()

    class Meta:
        model = VideoAttachment


class TextAttachmentFactory(factory.django.DjangoModelFactory):
    text = factory.Faker("text")

    class Meta:
        model = TextAttachment
