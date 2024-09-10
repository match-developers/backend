from django.db import models
from accounts.models import User  # user 테이블과 연결

class Club(models.Model):
    name = models.CharField(max_length=255)  # 클럽 이름
    profile_photo = models.ImageField(upload_to='clubs/profile_photos/', null=True, blank=True)  # 프로필 사진
    bio = models.TextField(null=True, blank=True)  # 클럽 소개
    member_number = models.IntegerField(default=0)  # 멤버 수 (자동 계산됨)
    followers = models.JSONField(null=True, blank=True)  # 팔로워 목록 (JSON 형태)
    owner = models.ForeignKey(User, related_name="clubs_owned", on_delete=models.CASCADE)  # 클럽 소유자 (User 테이블과 연결)

    # 클럽 멤버들 (사용자가 클럽에 가입하거나 탈퇴할 때 사용)
    members = models.ManyToManyField(User, related_name="clubs_joined", blank=True)

    def __str__(self):
        return self.name

    def add_member(self, user):
        """
        사용자가 클럽에 가입할 때 호출되는 메서드.
        """
        if user not in self.members.all():
            self.members.add(user)
            self.member_number = self.members.count()  # 멤버 수 갱신
            self.save()

    def remove_member(self, user):
        """
        사용자가 클럽에서 탈퇴할 때 호출되는 메서드.
        """
        if user in self.members.all():
            self.members.remove(user)
            self.member_number = self.members.count()  # 멤버 수 갱신
            self.save()