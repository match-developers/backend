from django.db import models
from . import League
from matchmaking.models import Match
from clubs.models import Team

class LeagueMatch(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)  # 리그와의 관계
    match = models.ForeignKey(Match, on_delete=models.CASCADE)  # 매치와의 관계
    home_team = models.ForeignKey(Team, related_name="home_league_matches", on_delete=models.CASCADE)  # 홈팀
    away_team = models.ForeignKey(Team, related_name="away_league_matches", on_delete=models.CASCADE)  # 원정팀
    round_number = models.IntegerField()  # 해당 매치가 몇 번째 라운드인지

    class Meta:
        unique_together = ('league', 'match')  # 리그와 매치의 조합이 유일함을 보장

    def __str__(self):
        return f"Match {self.match.id} in {self.league.league_name}: {self.home_team} vs {self.away_team}"