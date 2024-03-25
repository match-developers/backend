import factory
import factory.fuzzy

from sportsgrounds.models import SportGround, SportGroundGallery


class SportGroundFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    location = factory.Faker("point")
    description = factory.Faker("text")

    class Meta:
        model = SportGround


class SportGroundGalleryFactory(factory.django.DjangoModelFactory):
    image = factory.django.ImageField()
    description = factory.Faker("text")
    sportground = factory.SubFactory(SportGroundFactory)

    class Meta:
        model = SportGroundGallery
