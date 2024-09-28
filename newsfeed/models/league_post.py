from django.db import models
from newsfeed.models.newsfeed import NewsfeedPost  # 여전히 뉴스피드 포스트는 임포트
# League와 User는 문자열 참조 방식으로 대체

class LeaguePost(models.Model):
    league = models.ForeignKey('leagues.League', on_delete=models.CASCADE, related_name="league_posts")
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    post_content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="league_post")

    def __str__(self):
        return f"League Post for {self.league.league_name} by {self.created_by.username}"

    def get_league_details(self):
        return {
            "league_name": self.league.league_name,
            "current_round": self.league.current_round,
            "total_rounds": self.league.total_number_of_rounds,
            "participants": [team.name for team in self.league.participants.all()],
            "status": self.league_status(),
        }

    def league_status(self):
        LeagueStatus = models.get_model('leagues', 'LeagueStatus')  # 문자열 참조로 LeagueStatus 불러오기
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