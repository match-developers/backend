from django.db import models
from newsfeed.models.newsfeed import NewsfeedPost  # 여전히 뉴스피드 포스트는 임포트
# Match와 User는 문자열 참조 방식으로 대체

class MatchPost(models.Model):
    match = models.ForeignKey('matchmaking.Match', on_delete=models.CASCADE, related_name="match_posts")  # 문자열 참조 방식
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)  # 문자열 참조 방식
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