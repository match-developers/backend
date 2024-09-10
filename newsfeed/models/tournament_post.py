from django.db import models
from tournaments.models import Tournament, TournamentStatus
from newsfeed.models import NewsfeedPost
from accounts.models import User

class TournamentPost(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="tournament_posts")  # 관련된 토너먼트
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 포스트 작성자
    post_content = models.TextField(blank=True, null=True)  # 포스트 내용 (토너먼트 요약 등)
    created_at = models.DateTimeField(auto_now_add=True)  # 포스트 생성 시간

    # NewsfeedPost와 연결 (좋아요, 댓글, 공유 등은 NewsfeedPost에서 관리)
    newsfeed_post = models.OneToOneField(NewsfeedPost, on_delete=models.CASCADE, related_name="tournament_post")

    def __str__(self):
        return f"Tournament Post for {self.tournament.tournament_name} by {self.created_by.username}"

    def get_tournament_details(self):
        """
        토너먼트 세부 정보를 가져오는 메서드.
        """
        return {
            "tournament_name": self.tournament.tournament_name,
            "current_round": self.tournament.current_round,
            "total_rounds": self.tournament.total_number_of_match_rounds,
            "participants": [team.name for team in self.tournament.participants.all()],
            "status": self.tournament_status(),
        }

    def tournament_status(self):
        """
        토너먼트 상태 정보 가져오기 (진행 상태, 승/패 기록 등).
        """
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