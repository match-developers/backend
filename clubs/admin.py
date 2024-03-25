from django.contrib.gis import admin

from .models import (
    Club,
    ClubGallery,
    ClubNewMemberPost,
    ClubQuitPost,
    ClubTransferDonePost,
    ClubTransferInterestPost,
    ClubTransferInvitePost,
)


class ClubGalleryInline(admin.StackedInline):
    model = ClubGallery
    extra = 1  # Number of extra forms to display


class ClubAdmin(admin.OSMGeoAdmin):
    inlines = [ClubGalleryInline]


admin.site.register(Club, ClubAdmin)

admin.site.register(ClubNewMemberPost)
admin.site.register(ClubQuitPost)
admin.site.register(ClubTransferDonePost)
admin.site.register(ClubTransferInterestPost)
admin.site.register(ClubTransferInvitePost)
