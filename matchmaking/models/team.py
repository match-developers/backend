from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=255)  # 팀 이름 (자동 생성)
    club = models.ForeignKey('clubs.Club', null=True, blank=True, on_delete=models.CASCADE)  # Club을 문자열 참조로 변경
    is_red_team = models.BooleanField(default=True)  # Red Team, Blue Team 여부 (랜덤 경기일 경우에만 사용)

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
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)  # User를 문자열 참조로 변경
    is_starting_player = models.BooleanField(default=True)  # 선발 선수 여부

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.position})"