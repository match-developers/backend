from django.db import models
from clubs.models import Club
from leagues.models import League  # 리그 테이블과 연결
from tournaments.models import Tournament  # 토너먼트 테이블과 연결

class ClubStatistics(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE)  # Club과 1:1 관계
    mp = models.IntegerField(default=0)  # 경기 수
    wins = models.IntegerField(default=0)  # 승리 횟수
    draws = models.IntegerField(default=0)  # 무승부 횟수
    losses = models.IntegerField(default=0)  # 패배 횟수
    points_scored = models.IntegerField(default=0)  # 득점
    manner = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 매너 점수
    performance = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 성과 점수
    reviews = models.TextField(blank=True, null=True)  # 클럽에 대한 리뷰

    # 클럽의 플레이 스타일
    playstyle = models.CharField(max_length=255, blank=True, null=True)

    # 리그와 토너먼트 기록
    league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 리그
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 토너먼트

    def __str__(self):
        return f"{self.club.name} - Statistics"