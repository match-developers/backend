from django.db import models
from clubs.models.clubs import Club
from accounts.models.users import User

class Member(models.Model):
    """
    클럽의 멤버를 관리하는 모델.
    멤버의 역할(주전/교체/기타)까지 포함.
    """
    ROLE_CHOICES = [
        ('starter', 'Starter'),
        ('substitute', 'Substitute'),
        ('other', 'Other'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="members")  # 클럽과 연결
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 멤버인 유저
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')  # 멤버의 역할(선발, 교체, 기타)

    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.role})"


class Lineup(models.Model):
    """
    라인업을 관리하는 모델.
    선발 멤버와 포메이션을 관리.
    """
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="lineups")  # 클럽과 연결
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 라인업을 만든 사람
    starters = models.ManyToManyField(Member, related_name='starters')  # 선발 멤버들
    substitutes = models.ManyToManyField(Member, related_name='substitutes')  # 교체 멤버들
    
    # 포메이션 위치 정보 (JSON 형태로 선발 멤버들의 아이콘 좌표를 저장)
    formation_positions = models.JSONField(default=dict, blank=True)  # {"player_id": {"x": x좌표, "y": y좌표}}

    def __str__(self):
        return f"{self.club.name} - Lineup by {self.created_by.username}"

    def set_lineup(self, starters, substitutes, formation_positions):
        """
        라인업 및 포메이션을 설정하는 메서드.
        포메이션은 선수들의 아이콘 좌표를 저장함.
        """
        self.starters.set(starters)
        self.substitutes.set(substitutes)
        self.formation_positions = formation_positions  # 아이콘 좌표 저장
        self.save()

    def get_formation_positions(self):
        """
        포메이션 아이콘 위치를 불러오는 메서드.
        """
        return self.formation_positions


class Tactic(models.Model):
    """
    클럽의 전술을 관리하는 모델.
    전술에 대한 설명과 여러 전술을 추가 및 관리할 수 있음.
    """
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="tactics")  # 클럽과 연결
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 전술을 만든 사람
    name = models.CharField(max_length=255)  # 전술의 이름
    tactic_explanation = models.TextField(blank=True, null=True)  # 전술 설명
    created_at = models.DateTimeField(auto_now_add=True)  # 전술 생성일
    updated_at = models.DateTimeField(auto_now=True)  # 전술 수정일

    def __str__(self):
        return f"{self.club.name} - {self.name} by {self.created_by.username}"

    def update_tactic(self, name, explanation):
        """
        전술의 이름과 설명을 업데이트하는 메서드.
        """
        self.name = name
        self.tactic_explanation = explanation
        self.save()

    def delete_tactic(self):
        """
        전술을 삭제하는 메서드.
        """
        self.delete()