from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from accounts.models.users import User, UserStatistics
from matchmaking.models.match import Match, WinningMethod
from matchmaking.models.team import Team, TeamPlayer
from newsfeed.models.newsfeed import NewsfeedPost
from newsfeed.models.tournament_post import TournamentPost


class Tournament(models.Model):
    TOURNAMENT_TYPES = [
        ('club', 'Club'),
        ('individual', 'Individual'),
    ]
    
    SCHEDULING_TYPES = [
        ('organizer_based', 'Organizer Based'),
        ('deadline_based', 'Deadline Based'),
    ]
    
    ROUND_CHOICES = [
        ('16강', 'Round of 16'),
        ('8강', 'Quarterfinals'),
        ('4강', 'Semifinals'),
        ('결승', 'Final'),
    ]
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament_name = models.CharField(max_length=255)
    description = models.TextField()
    tournament_type = models.CharField(max_length=50, choices=TOURNAMENT_TYPES, default='individual')
    participants = models.ManyToManyField(Team, related_name="tournaments")
    
    total_number_of_rounds = models.IntegerField()  # 총 라운드 수
    max_teams = models.IntegerField()  # 참가 팀 수
    start_date = models.DateField()  # 시작일
    deadline = models.DateField()  # 마감일
    current_round = models.CharField(max_length=50, choices=ROUND_CHOICES, default='16강')  # 현재 라운드
    scheduling_type = models.CharField(max_length=50, choices=SCHEDULING_TYPES, default='organizer_based')
    match_duration = models.DurationField()  # 경기 시간
    winning_method = models.ForeignKey(WinningMethod, on_delete=models.SET_NULL, null=True, blank=True)  # 승리 조건

    def __str__(self):
        return self.tournament_name

    def generate_bracket(self):
        """
        토너먼트 대진표를 생성. 첫 라운드에서 팀들을 섞어 매치업을 구성.
        """
        teams = list(self.participants.all())
        if len(teams) != self.max_teams:
            raise ValidationError("참가 팀 수가 충분하지 않습니다.")
        
        num_teams = len(teams)
        bracket = []
        
        while len(teams) > 1:
            round_matches = []
            for i in range(0, num_teams - 1, 2):
                home_team = teams[i]
                away_team = teams[i + 1]
                match = Match.objects.create(
                    home_team=home_team,
                    away_team=away_team,
                    match_type='tournament',
                    status='scheduled',
                    duration=self.match_duration,
                    winning_method=self.winning_method
                )
                round_matches.append(match)
            bracket.append(round_matches)
            teams = teams[:num_teams // 2]  # 다음 라운드를 위해 팀을 절반으로 줄임

        return bracket

    def advance_round(self):
        """
        현재 라운드를 마친 후 다음 라운드를 진행.
        """
        if self.current_round < self.total_number_of_rounds:
            self.current_round += 1
        else:
            raise ValidationError("토너먼트가 이미 종료되었습니다.")
        self.save()

    def validate_join(self, user):
        """
        토너먼트 시작 후에는 참가할 수 없도록 검증.
        """
        if self.start_date < timezone.now().date():
            raise ValidationError("토너먼트가 시작된 후에는 참가할 수 없습니다.")
        
        if self.participants.count() >= self.max_teams:
            raise ValidationError("이 토너먼트는 참가 인원이 가득 찼습니다.")

        return True
    
    # post creation methods
    def create_tournament_post(self):
        """
        토너먼트 생성 시, 뉴스피드에 포스트를 생성하는 메서드.
        """
        # 뉴스피드 포스트 생성
        newsfeed_post = NewsfeedPost.objects.create(
            newsfeed=self.organizer.newsfeed,  # 토너먼트 주최자의 뉴스피드에 추가
            post_type="tournament",
            post_id=self.id,
            post_content=f"Tournament {self.tournament_name} has been created! Join now!"
        )

        # 토너먼트 포스트 생성
        TournamentPost.objects.create(
            tournament=self,
            created_by=self.organizer,
            post_content=f"Tournament {self.tournament_name} has been created!",
            newsfeed_post=newsfeed_post
        )

    def update_tournament_post_on_full_participation(self):
        """
        토너먼트 참가 인원이 꽉 찼을 때 뉴스피드 포스트 업데이트
        """
        if self.participants.count() >= self.max_teams:  # 모든 팀이 참여했을 때
            newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="tournament")
            newsfeed_post.post_content = f"Tournament {self.tournament_name} is now full! The games will begin soon."
            newsfeed_post.save()

    def update_tournament_post_on_round_completion(self):
        """
        각 라운드가 완료되었을 때 뉴스피드 포스트 업데이트
        """
        newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="tournament")
        newsfeed_post.post_content = f"Round {self.current_round} of Tournament {self.tournament_name} is now complete!"
        newsfeed_post.save()

    def update_tournament_post_on_completion(self):
        """
        토너먼트가 완료되었을 때 최종 결과를 뉴스피드 포스트로 업데이트
        """
        newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="tournament")
        newsfeed_post.post_content = f"Tournament {self.tournament_name} has been completed! Congratulations to the winners!"
        newsfeed_post.save()
class TournamentStatus(models.Model):
    ROUND_CHOICES = [
        ('16강', 'Round of 16'),
        ('8강', 'Quarterfinals'),
        ('4강', 'Semifinals'),
        ('결승', 'Final'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    current_round = models.CharField(max_length=50, choices=ROUND_CHOICES, default='16강')  # 선택 가능한 라운드
    advancement_status = models.CharField(max_length=50, choices=[
        ('in_progress', 'In Progress'),
        ('eliminated', 'Eliminated'),
        ('winner', 'Winner')
    ], default='in_progress')
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    matches_played = models.IntegerField(default=0)
    final_position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Team {self.team.name} in {self.tournament.tournament_name} - {self.current_round}"

    def update_status(self, win=False):
        """
        경기 결과에 따라 팀의 상태를 업데이트.
        """
        self.matches_played += 1
        if win:
            self.wins += 1
        else:
            self.losses += 1

        # 팀 탈락 여부 확인
        if self.losses >= 1 and self.tournament.scheduling_type == 'knockout':
            self.advancement_status = 'eliminated'
        elif self.current_round == '결승' and win:
            self.advancement_status = 'winner'

        self.save()