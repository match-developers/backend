from django.contrib import admin

from .models import (
    FriendlyClubMatch,
    Goal,
    Match,
    MatchParticipant,
    MatchPost,
    MatchScore,
)

admin.site.register(Match)
admin.site.register(MatchParticipant)
admin.site.register(MatchScore)
admin.site.register(Goal)
admin.site.register(FriendlyClubMatch)
admin.site.register(MatchPost)
