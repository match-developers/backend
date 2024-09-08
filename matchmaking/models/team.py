from django.db import models
from accounts.models import User  # User 모델 참조
from clubs.models import Club  # Club 모델 참조

class Team(models.Model):
    name = models.CharField(max_length=255)  # 팀 이름 (자동 생성)
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)  # 클럽 소속 팀일 경우
    is_red_team = models.BooleanField(default=True)  # Red Team, Blue Team 여부 (랜덤 경기일 경우에만 사용)
    formation = models.TextField(null=True, blank=True)  # 포메이션 (유저들이 설정한 포지션 정보)

    def __str__(self):
        # 팀 이름 자동 생성 (클럽 소속 팀이면 클럽 이름, 아니면 레드팀/블루팀/개인 유저 이름)
        if self.club:
            return f"{self.club.name} 팀"
        elif self.name:
            return self.name
        else:
            return "Red Team" if self.is_red_team else "Blue Team"
        
class TeamPlayer(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # 팀과 연결
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 플레이어
    position = models.CharField(max_length=50, null=True, blank=True)  # 플레이어의 포지션 (빈 직사각형 템플릿 위에 표시될 위치)

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.position})"