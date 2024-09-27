from django.db import models
from accounts.models.users import User
from newsfeed.models.newsfeed import NewsfeedPost
from tournaments.models.tournament import TournamentStatus

class TournamentPost(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name="tournament_posts")  # 문자열 참조 방식
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 포스트 작성자
    post_content = models.TextField(blank=True, null=True)  # 포스트 내용 (토너먼트 요약 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="tournament_post")  # 뉴스피드 포스트와 연결

    def __str__(self):
        return f"Tournament Post for {self.tournament.tournament_name} by {self.created_by.username}"

    def get_tournament_details(self):
        return {
            "tournament_name": self.tournament.tournament_name,
            "current_round": self.tournament.current_round,
            "total_rounds": self.tournament.total_number_of_match_rounds,
            "participants": [team.name for team in self.tournament.participants.all()],
            "status": self.tournament_status(),
        }

    def tournament_status(self):
        statuses = TournamentStatus.objects.filter(tournament=self.tournament)
        return [
            {
                "team": status.team.name,
                "current_round": status.current_round,
                "advancement_status": status.advancement_status,
                "wins": status.wins,
                "losses": status.losses,
                "matches_played": status.matches_played,
            }
            for status in statuses
        ]