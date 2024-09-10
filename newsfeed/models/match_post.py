from django.db import models
from matchmaking.models import Match
from newsfeed.models import NewsfeedPost
from accounts.models import User

class MatchPost(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="match_posts")  # 관련된 매치
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 포스트 생성자
    post_content = models.TextField(blank=True, null=True)  # 포스트 내용 (경기 요약 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 포스트 생성 시간

    # NewsfeedPost와 연결 (좋아요, 댓글, 공유 등은 NewsfeedPost에서 관리)
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="match_post")

    def __str__(self):
        return f"Match Post for {self.match} by {self.created_by.username}"

    def get_match_details(self):
        """
        매치의 세부 정보를 가져오는 메서드.
        """
        return {
            "match_time": self.match.start_time,
            "players": [player.user.username for player in self.match.participants.all()],
            "score": f"{self.match.score.home_score} - {self.match.score.away_score}",
            "location": self.match.sports_ground.name,
        }