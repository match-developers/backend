from django.db import models
from accounts.models import User


class Newsfeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 뉴스피드 소유자 (유저)
    created_at = models.DateTimeField(auto_now_add=True)  # 뉴스피드 생성 시간

    def __str__(self):
        return f"Newsfeed of {self.user.username}"


class NewsfeedPost(models.Model):
    NEWSFEED_POST_TYPES = [
        ('match', 'Match Post'),
        ('league', 'League Post'),
        ('tournament', 'Tournament Post'),
        ('transfer', 'Transfer Post'),
    ]

    newsfeed = models.ForeignKey(Newsfeed, on_delete=models.CASCADE, related_name="posts")  # 뉴스피드와 연결
    post_type = models.CharField(max_length=50, choices=NEWSFEED_POST_TYPES)  # 포스트 유형
    post_id = models.IntegerField()  # 연결된 포스트의 ID (Match, League, Tournament, Transfer 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 포스트 생성 시간

    likes = models.IntegerField(default=0)  # 좋아요 수
    comments = models.JSONField(default=list)  # 댓글 목록 (JSON 필드)
    shares = models.IntegerField(default=0)  # 공유 수
    edited_at = models.DateTimeField(null=True, blank=True)  # 수정된 시간

    def __str__(self):
        return f"{self.post_type.capitalize()} Post in {self.newsfeed.user.username}'s newsfeed"

    def edit_post(self, new_content):
        """
        포스트를 수정하는 메서드 (여기서는 실제로 포스트 내용을 수정하는 것은 다른 모델에서 관리할 수 있음).
        """
        self.edited_at = models.DateTimeField(auto_now=True)
        # 실제 내용은 post_id와 연결된 포스트 모델에서 수정해야 함.
        self.save()

    def add_like(self):
        """
        좋아요를 추가하는 메서드.
        """
        self.likes += 1
        self.save()

    def add_comment(self, comment):
        """
        댓글을 추가하는 메서드.
        """
        self.comments.append(comment)
        self.save()

    def add_share(self):
        """
        공유 수를 증가시키는 메서드.
        """
        self.shares += 1
        self.save()