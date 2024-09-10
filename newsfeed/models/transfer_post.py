from django.db import models
from clubs.models import Club
from accounts.models import User
from newsfeed.models import NewsfeedPost

class TransferPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 클럽에 가입하거나 탈퇴한 사용자
    club = models.ForeignKey(Club, on_delete=models.CASCADE)  # 관련된 클럽
    transfer_type = models.CharField(max_length=50, choices=[('join', 'Join'), ('quit', 'Quit')])  # 전송 유형 (가입/탈퇴)
    created_at = models.DateTimeField(auto_now_add=True)  # 포스트 생성 시간

    # NewsfeedPost와 연결 (좋아요, 댓글, 공유 등은 NewsfeedPost에서 관리)
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="transfer_post")

    def __str__(self):
        action = "joined" if self.transfer_type == "join" else "left"
        return f"{self.user.username} has {action} the club {self.club.name}"