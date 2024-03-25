import factory
import factory.fuzzy

from leagues.models import (
    League,
    LeagueMatch,
    LeaguePosition,
    LeagueRound,
    LeagueTablePost,
)


class LeagueFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    season = factory.Faker("name")

    class Meta:
        model = League


class LeagueRoundFactory(factory.django.DjangoModelFactory):
    league = factory.SubFactory(LeagueFactory)
    name = factory.Faker("name")

    class Meta:
        model = LeagueRound


class LeagueMatchFactory(factory.django.DjangoModelFactory):
    round = factory.SubFactory(LeagueRoundFactory)
    home = factory.SubFactory("clubs.tests.factories.ClubFactory")
    away = factory.SubFactory("clubs.tests.factories.ClubFactory")
    match = factory.SubFactory("matchmaking.tests.factories.MatchFactory")

    class Meta:
        model = LeagueMatch


class LeaguePositionFactory(factory.django.DjangoModelFactory):
    league = factory.SubFactory(LeagueFactory)
    club = factory.SubFactory("clubs.tests.factories.ClubFactory")
    position = factory.fuzzy.FuzzyInteger(0, 20)
    points = factory.fuzzy.FuzzyInteger(0, 60)
    played = factory.fuzzy.FuzzyInteger(0, 20)
    won = factory.fuzzy.FuzzyInteger(0, 20)
    drawn = factory.fuzzy.FuzzyInteger(0, 20)
    lost = factory.fuzzy.FuzzyInteger(0, 20)
    goals_for = factory.fuzzy.FuzzyInteger(0, 60)
    goals_against = factory.fuzzy.FuzzyInteger(0, 60)
    goal_difference = factory.fuzzy.FuzzyInteger(-60, 60)

    class Meta:
        model = LeaguePosition


class LeagueTablePostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    league = factory.SubFactory(LeagueFactory)

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = LeagueTablePost
