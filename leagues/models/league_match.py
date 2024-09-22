from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from .league import League
from matchmaking.models.match import Match
from matchmaking.models.team import Team

class LeagueMatch(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name="home_league_matches", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_league_matches", on_delete=models.CASCADE)
    round_number = models.IntegerField()
    match_date = models.DateField(null=True, blank=True)
    match_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('league', 'match')
    
    def schedule_match(self):
        if self.league.scheduling_type == 'organizer_based':
            if not self.match_date or not self.match_time:
                raise ValidationError("Organizer must set the match date and time.")
        elif self.league.scheduling_type == 'deadline_based':
            if not self.match_date or not self.match_time:
                if timezone.now().date() > self.league.deadline:
                    raise ValidationError("The match deadline has passed.")
        else:
            raise ValidationError("Unknown scheduling type.")
    
    def __str__(self):
        return f"Match {self.match.id} in {self.league.league_name}: {self.home_team} vs {self.away_team}"