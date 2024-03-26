from django.core.management.base import BaseCommand

from accounts.tests.factories import AccountFactory
from clubs.tests.factories import ClubFactory
from leagues.tests.factories import LeagueFactory
from sportsgrounds.tests.factories import SportGroundFactory
from tournaments.tests.factories import TournamentFactory


class Command(BaseCommand):
    help = "Create factory data for the project"

    def handle(self, *args, **options):
        # Create 500 accounts
        AccountFactory.create_batch(5000)

        # Create 100 clubs
        ClubFactory.create_batch(100)

        # Create 100 sportsgrounds
        SportGroundFactory.create_batch(100)

        # Create 1 League
        LeagueFactory.create_batch(10)

        # Create 1 Tournament
        TournamentFactory.create_batch(10)

        self.stdout.write(
            self.style.SUCCESS("Successfully created factory data for the project")
        )
