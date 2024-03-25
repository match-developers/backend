import factory
import factory.fuzzy

from sportsgrounds.models import SportGround, SportGroundGallery


class SportGroundFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    location = factory.Faker("point")
    description = factory.Maybe(
        "should_have_description",
        yes_declaration=factory.Faker("text"),
        no_declaration=None,
    )

    class Meta:
        model = SportGround

    class Params:
        should_have_description = factory.Faker("boolean")


class SportGroundGalleryFactory(factory.django.DjangoModelFactory):
    image = factory.django.ImageField()
    description = factory.Maybe(
        "should_have_description",
        yes_declaration=factory.Faker("text"),
        no_declaration=None,
    )
    sportground = factory.SubFactory(SportGroundFactory)

    class Meta:
        model = SportGroundGallery

    class Params:
        should_have_description = factory.Faker("boolean")
