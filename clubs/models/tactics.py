from django.db import models
from clubs.models import Club

class Tactic(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="tactics")  # Club과 1:N 관계
    member_list = models.JSONField(blank=True, null=True)  # 팀원 리스트 (JSON 형식)
    lineup = models.TextField(blank=True, null=True)  # 라인업 설명
    tactic_explanation = models.TextField(blank=True, null=True)  # 전술 설명

    def __str__(self):
        return f"{self.club.name} - Tactics"