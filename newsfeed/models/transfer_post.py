from django.db import models
from newsfeed.models.newsfeed import NewsfeedPost

class TransferPost(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)  # 문자열로 User 모델 참조
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE)  # 클럽 참조
    transfer_type = models.CharField(max_length=50, choices=[('join', 'Join'), ('quit', 'Quit')])  # 가입/탈퇴 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="transfer_post")  # 뉴스피드 포스트와 연결

    def __str__(self):
        action = "joined" if self.transfer_type == "join" else "left"
        return f"{self.user.username} has {action} the club {self.club.name}"