import factory
import factory.fuzzy

from matchmaking.choices import MATCH_TYPES, STATUS_CHOICES
from matchmaking.models import (
    Goal,
    Match,
    MatchParticipant,
    MatchPost,
    MatchScore,
    SportPosition,
)
from sports.choices import SPORT_CHOICES


class SportPositionFactory(factory.django.DjangoModelFactory):
    sport = factory.fuzzy.FuzzyChoice([x[0] for x in SPORT_CHOICES])
    description = factory.Faker("text")

    class Meta:
        model = SportPosition


class MatchParticipantFactory(factory.django.DjangoModelFactory):
    player = factory.SubFactory("accounts.tests.factories.AccountFactory")
    club = factory.SubFactory("clubs.tests.factories.ClubFactory")
    position = factory.SubFactory(SportPositionFactory)
    is_home_team = factory.Faker("boolean")

    class Meta:
        model = MatchParticipant


class MatchFactory(factory.django.DjangoModelFactory):
    sports_ground = factory.SubFactory(
        "sportsgrounds.tests.factories.SportGroundFactory"
    )
    sport = factory.Faker("word")
    creator = factory.SubFactory("accounts.tests.factories.AccountFactory")
    start_time = factory.Faker("date_time")
    duration = factory.Faker("time_delta")
    is_public = factory.Faker("boolean")
    is_club = factory.Faker("boolean")
    total_spots = factory.fuzzy.FuzzyInteger(0, 22)
    average_level = factory.fuzzy.FuzzyInteger(1, 10)
    home = factory.SubFactory("clubs.tests.factories.ClubFactory")
    away = factory.SubFactory("clubs.tests.factories.ClubFactory")
    status = factory.fuzzy.FuzzyChoice([x[0] for x in STATUS_CHOICES])
    match_type = factory.fuzzy.FuzzyChoice([x[0] for x in MATCH_TYPES])

    participants = factory.RelatedFactoryList(
        MatchParticipantFactory,
        factory_related_name="match",
        size=2,
    )

    class Meta:
        model = Match


class MatchScoreFactory(factory.django.DjangoModelFactory):
    match = factory.SubFactory(MatchFactory)
    home_score = factory.fuzzy.FuzzyInteger(0, 100)
    away_score = factory.fuzzy.FuzzyInteger(0, 300)

    class Meta:
        model = MatchScore


class GoalFactory(factory.django.DjangoModelFactory):
    match = factory.SubFactory(MatchFactory)
    scorer = factory.SubFactory("accounts.tests.factories.AccountFactory")
    time_scored = factory.Faker("date_time")
    is_penalty = factory.Faker("boolean")
    is_own_goal = factory.Faker("boolean")

    class Meta:
        model = Goal


class MatchPostFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text")
    user = factory.SubFactory("accounts.tests.factories.AccountFactory")
    match = factory.SubFactory(MatchFactory)

    comments = factory.RelatedFactory("newsfeed.tests.factories.CommentFactory")
    likes = factory.RelatedFactory("newsfeed.tests.factories.LikeFactory")

    class Meta:
        model = MatchPost
