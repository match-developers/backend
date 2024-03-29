from django.contrib.gis.geos import Point

import factory
import factory.fuzzy
from faker import Faker

from sportsgrounds.models import SportGround, SportGroundGallery

fake = Faker()


class SportGroundFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    location = factory.LazyAttribute(
        lambda _: Point(float(fake.longitude()), float(fake.latitude()))
    )
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
