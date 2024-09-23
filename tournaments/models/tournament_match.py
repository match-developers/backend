from django.core.exceptions import ValidationError
from django.utils import timezone

from django.db import models
from .tournament import Tournament
from matchmaking.models.match import Match
from matchmaking.models.team import Team

class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name="home_tournament_matches", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_tournament_matches", on_delete=models.CASCADE)
    round_number = models.CharField(max_length=50)  # 예: '16강', '8강', '준결승', '결승'
    match_date = models.DateField(null=True, blank=True)
    match_time = models.TimeField(null=True, blank=True)
    is_knockout_stage = models.BooleanField(default=True)  # 토너먼트는 기본적으로 녹아웃 스테이지
    
    class Meta:
        unique_together = ('tournament', 'match')

    def schedule_match(self):
        """
        Organizer 또는 팀 리더가 매치 시간을 설정해야 함.
        """
        if self.tournament.scheduling_type == 'organizer_based':
            if not self.match_date or not self.match_time:
                raise ValidationError("Organizer는 매치 날짜와 시간을 설정해야 합니다.")
        elif self.tournament.scheduling_type == 'deadline_based':
            if not self.match_date or not self.match_time:
                if timezone.now().date() > self.tournament.deadline:
                    raise ValidationError("데드라인 전에 매치가 스케줄되지 않았습니다.")
        else:
            raise ValidationError("알 수 없는 스케줄링 타입입니다.")

    def __str__(self):
        return f"Match {self.match.id} in {self.tournament.tournament_name} - Round {self.round_number}: {self.home_team} vs {self.away_team}"