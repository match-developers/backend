from django.contrib import admin

from .models import Stage, Tournament, TournamentMatch

admin.site.register(Tournament)
admin.site.register(Stage)
admin.site.register(TournamentMatch)
