from django.db import models
from leagues.models import League, LeagueStatus
from newsfeed.models import NewsfeedPost
from accounts.models import User

class LeaguePost(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="league_posts")  # 관련된 리그
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 포스트 생성자
    post_content = models.TextField(blank=True, null=True)  # 포스트 내용 (리그 요약 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 포스트 생성 시간

    # NewsfeedPost와 연결 (좋아요, 댓글, 공유 등은 NewsfeedPost에서 관리)
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="league_post")

    def __str__(self):
        return f"League Post for {self.league.league_name} by {self.created_by.username}"

    def get_league_details(self):
        """
        리그의 세부 정보를 가져오는 메서드.
        """
        return {
            "league_name": self.league.league_name,
            "current_round": self.league.current_round,
            "total_rounds": self.league.total_number_of_rounds,
            "participants": [team.name for team in self.league.participants.all()],
            "status": self.league_status(),
        }

    def league_status(self):
        """
        리그 상태 정보 가져오기 (순위 등).
        """
        statuses = LeagueStatus.objects.filter(league=self.league)
        return [
            {
                "team": status.team.name,
                "position": status.current_position,
                "points": status.league_points,
                "wins": status.wins,
                "draws": status.draws,
                "losses": status.losses,
            }
            for status in statuses
        ]