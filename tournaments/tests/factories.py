import factory
import factory.fuzzy

from tournaments.choices import TOURNAMENT_STAGE_TYPES
from tournaments.models import Stage, Tournament, TournamentMatch


class TournamentFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = Tournament


class StageFactory(factory.django.DjangoModelFactory):
    tournament = factory.SubFactory(TournamentFactory)
    name = factory.Faker("word")
    type = factory.fuzzy.FuzzyChoice([x[0] for x in TOURNAMENT_STAGE_TYPES])

    class Meta:
        model = Stage


class TournamentMatchFactory(factory.django.DjangoModelFactory):
    stage = factory.SubFactory(StageFactory)
    match = factory.SubFactory("matchmaking.tests.factories.MatchFactory")

    class Meta:
        model = TournamentMatch
