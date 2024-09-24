from django.db import models
from matchmaking.models.match import Match
from newsfeed.models.newsfeed import NewsfeedPost
from accounts.models.users import User

class MatchPost(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="match_posts")  # 관련된 매치
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 포스트 생성자
    post_content = models.TextField(blank=True, null=True)  # 포스트 내용 (경기 요약 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="match_post")  # 뉴스피드 포스트와 연결

    def __str__(self):
        return f"Match Post for {self.match} by {self.created_by.username}"

    def get_match_details(self):
        return {
            "match_time": self.match.start_time,
            "players": [player.user.username for player in self.match.participants.all()],
            "score": f"{self.match.score.home_score} - {self.match.score.away_score}",
            "location": self.match.sports_ground.name,
        }