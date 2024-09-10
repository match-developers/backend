from django.db import models
from . import Tournament
from matchmaking.models import Match
from clubs.models import Team

class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)  # 토너먼트와의 관계
    match = models.ForeignKey(Match, on_delete=models.CASCADE)  # 매치와의 관계
    home_team = models.ForeignKey(Team, related_name="home_tournament_matches", on_delete=models.CASCADE)  # 홈팀
    away_team = models.ForeignKey(Team, related_name="away_tournament_matches", on_delete=models.CASCADE)  # 원정팀
    round_number = models.IntegerField()  # 해당 매치가 몇 번째 라운드인지
    is_knockout_stage = models.BooleanField(default=False)  # 이 매치가 토너먼트의 녹아웃 스테이지인지 여부
    advancement_status = models.CharField(max_length=50, choices=[('win', 'Win'), ('loss', 'Loss'), ('draw', 'Draw')], default='draw')  # 팀의 진출 상태

    class Meta:
        unique_together = ('tournament', 'match')  # 토너먼트와 매치의 조합이 유일함을 보장

    def __str__(self):
        return f"Match {self.match.id} in {self.tournament.tournament_name}: {self.home_team} vs {self.away_team}"