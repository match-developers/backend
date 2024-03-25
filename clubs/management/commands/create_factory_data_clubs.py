from django.core.management.base import BaseCommand

from clubs.tests.factories import (
    ClubFactory,
    ClubGalleryFactory,
    ClubNewMemberPostFactory,
    ClubQuitPostFactory,
    ClubTransferDonePostFactory,
    ClubTransferInterestPostFactory,
    ClubTransferInvitePostFactory,
)


class Command(BaseCommand):
    help = "Create factory data for the clubs app"

    def handle(self, *args, **options):
        ClubFactory.create_batch(30)
        ClubGalleryFactory.create_batch(10)
        ClubTransferInvitePostFactory.create_batch(10)
        ClubTransferDonePostFactory.create_batch(10)
        ClubTransferInterestPostFactory.create_batch(10)
        ClubQuitPostFactory.create_batch(10)
        ClubNewMemberPostFactory.create_batch(10)

        self.stdout.write(
            self.style.SUCCESS("Successfully created factory data for the clubs app")
        )
