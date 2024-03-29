import factory
import factory.fuzzy

from sports.choices import SPORT_CHOICES
from sports.models import SportPosition


class SportPositionFactory(factory.django.DjangoModelFactory):
    sport = factory.fuzzy.FuzzyChoice([x[0] for x in SPORT_CHOICES])
    position_name = factory.Faker("word")

    class Meta:
        model = SportPosition
