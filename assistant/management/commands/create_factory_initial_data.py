from django.core.management.base import BaseCommand

from accounts.tests.factories import AccountFactory
from clubs.tests.factories import ClubFactory
from leagues.tests.factories import (
    LeagueFactory,
    LeagueMatchFactory,
    LeagueRoundFactory,
)
from matchmaking.tests.factories import MatchFactory, MatchParticipantFactory
from sports.tests.factories import SportPositionFactory
from sportsgrounds.tests.factories import SportGroundFactory
from tournaments.tests.factories import TournamentFactory


class Command(BaseCommand):
    help = "Create factory data for the project"

    def handle(self, *args, **options):
        # Create 500 accounts
        account_factories = AccountFactory.create_batch(300)

        # Create 100 clubs
        club_factories = ClubFactory.create_batch(100)

        # Create 100 sportsgrounds
        sportground_factories = SportGroundFactory.create_batch(100)

        # Create 1 League with their respectives matches
        league = LeagueFactory.create()
        # Create 1 League Round
        league_round = LeagueRoundFactory.create(league=league)

        club_home = club_factories[0]
        club_away = club_factories[1]

        league.clubs.add(club_home)
        league.clubs.add(club_away)

        match = MatchFactory.create(
            sports_ground=sportground_factories[0],
            is_public=True,
            is_club=True,
            home=club_home,
            away=club_away,
            match_type="league",
        )
        league_match = LeagueMatchFactory.create(
            round=league_round,
            match=match,
        )

        for pl_idx in range(11):
            for cl_idx in range(2):
                club_involved = club_home if cl_idx == 0 else club_away
                club_involved.members.add(account_factories[pl_idx * 2 + cl_idx])
                league_match.match.participants.add(
                    MatchParticipantFactory.create(
                        player=account_factories[pl_idx * 2 + cl_idx],
                        club=club_involved,
                        position=SportPositionFactory.create(),
                    )
                )

        # Create 1 Tournament
        # TournamentFactory.create_batch(10)

        self.stdout.write(
            self.style.SUCCESS("Successfully created factory data for the project")
        )
