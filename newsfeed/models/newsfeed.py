from django.db import models

# User 모델에 문자열 참조 방식 사용
class Newsfeed(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)  # 문자열 참조로 User 참조
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Newsfeed of {self.user.username}"


class NewsfeedPost(models.Model):
    NEWSFEED_POST_TYPES = [
        ('match', 'Match Post'),
        ('league', 'League Post'),
        ('tournament', 'Tournament Post'),
        ('transfer', 'Transfer Post'),
    ]

    newsfeed = models.ForeignKey(Newsfeed, on_delete=models.CASCADE, related_name="posts")
    post_type = models.CharField(max_length=50, choices=NEWSFEED_POST_TYPES)
    post_id = models.IntegerField()  # 연결된 포스트의 ID (Match, League, Tournament, Transfer 등)
    created_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    comments = models.JSONField(default=list)
    shares = models.IntegerField(default=0)
    edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.post_type.capitalize()} Post in {self.newsfeed.user.username}'s newsfeed"

    def add_like(self):
        """좋아요 추가"""
        self.likes += 1
        self.save()

    def add_comment(self, comment):
        """댓글 추가"""
        self.comments.append(comment)
        self.save()

    def add_share(self):
        """공유 수 증가"""
        self.shares += 1
        self.save()

    def edit_post(self, new_content):
        """포스트 수정 (여기서는 내용 수정 대신 수정 시간만 기록)"""
        self.edited_at = models.DateTimeField(auto_now=True)
        self.save()