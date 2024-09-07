from django.db import models
from accounts.models import User  # user 테이블과 연결

class Club(models.Model):
    name = models.CharField(max_length=255)  # 클럽 이름
    profile_photo = models.ImageField(upload_to='clubs/profile_photos/', null=True, blank=True)  # 프로필 사진
    bio = models.TextField(null=True, blank=True)  # 클럽 소개
    member_number = models.IntegerField(default=0)  # 멤버 수
    followers = models.JSONField(null=True, blank=True)  # 팔로워 목록 (JSON 형태)
    owner = models.ForeignKey(User, related_name="clubs_owned", on_delete=models.CASCADE)  # 클럽 소유자 (User 테이블과 연결)

    def __str__(self):
        return self.name