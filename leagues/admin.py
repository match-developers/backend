from django.contrib import admin

from .models import League, LeagueMatch, LeaguePosition, LeagueRound

admin.site.register(League)
admin.site.register(LeagueMatch)
admin.site.register(LeaguePosition)
admin.site.register(LeagueRound)
