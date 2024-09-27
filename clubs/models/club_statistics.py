from django.db import models
from clubs.models.clubs import Club
from leagues.models.league import League  # 리그 테이블과 연결
from tournaments.models.tournament import Tournament  # 토너먼트 테이블과 연결
from accounts.models.users import UserStatistics  # 유저 통계와 연결

class ClubStatistics(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE)  # Club과 1:1 관계
    mp = models.IntegerField(default=0)  # 경기 수
    wins = models.IntegerField(default=0)  # 승리 횟수
    draws = models.IntegerField(default=0)  # 무승부 횟수
    losses = models.IntegerField(default=0)  # 패배 횟수
    points_scored = models.IntegerField(default=0)  # 득점
    manner = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 매너 점수 (멤버들의 평균)
    performance = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 성과 점수

    # 클럽의 플레이 스타일
    playstyle = models.CharField(max_length=255, blank=True, null=True)

    # 리그와 토너먼트 기록
    league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 리그
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 토너먼트

    def __str__(self):
        return f"{self.club.name} - Statistics"

    def update_match_stats(self, match_result, points):
        """
        클럽의 경기 통계를 업데이트하는 메서드.
        match_result: 'win', 'draw', 'loss' 중 하나.
        points: 해당 경기에서 클럽이 득점한 포인트.
        """
        self.mp += 1  # 총 경기 수 1 증가
        self.points_scored += points  # 득점 업데이트

        if match_result == 'win':
            self.wins += 1
        elif match_result == 'draw':
            self.draws += 1
        elif match_result == 'loss':
            self.losses += 1

        self.save()

    def update_manner_score(self):
        """
        클럽 멤버들의 평균 매너 점수를 계산하여 업데이트하는 메서드.
        """
        members = self.club.members.all()
        total_manner = 0
        member_count = members.count()

        for member in members:
            user_stats = UserStatistics.objects.get(user=member)
            total_manner += user_stats.manner

        if member_count > 0:
            self.manner = total_manner / member_count  # 멤버들의 평균 매너 점수
        else:
            self.manner = 0.00

        self.save()

    def update_performance_score(self):
        """
        클럽의 성과 점수를 업데이트하는 메서드. 
        클럽 멤버들의 성과 점수 평균을 기반으로 계산.
        """
        members = self.club.members.all()
        total_performance = 0
        member_count = members.count()

        for member in members:
            user_stats = UserStatistics.objects.get(user=member)
            total_performance += user_stats.performance

        if member_count > 0:
            self.performance = total_performance / member_count  # 멤버들의 평균 성과 점수
        else:
            self.performance = 0.00

        self.save()