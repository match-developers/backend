from model_utils.models import TimeStampedModel
from django.db import models
from accounts.models import User
from matchmaking.models import WinningMethod, Team, TeamPlayer

# League 모델
class League(TimeStampedModel):
    LEAGUE_TYPES = [
        ('club', 'Club'),
        ('individual', 'Individual'),
    ]
    
    SCHEDULING_TYPES = [
        ('organizer_based', 'Organizer Based'),
        ('deadline_based', 'Deadline Based'),
    ]
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)  # 리그 주최자
    league_name = models.CharField(max_length=255)
    description = models.TextField()
    
    winning_method = models.ForeignKey(WinningMethod, on_delete=models.SET_NULL, null=True, blank=True)  # 승리 조건
    match_duration = models.DurationField()  # 각 매치의 경기 시간
    
    league_type = models.CharField(max_length=50, choices=LEAGUE_TYPES, default='individual')  # 리그 타입
    participants = models.ManyToManyField(Team, related_name="leagues")  # 팀 또는 개인 (팀으로 취급)
    
    frequency = models.IntegerField()  # 경기 주기 (일 단위, 예: 7일에 한 번)
    total_number_of_rounds = models.IntegerField()  # 총 라운드 수
    current_round = models.IntegerField(default=1)  # 현재 라운드
    start_date = models.DateField()  # 리그 시작일
    end_date = models.DateField(null=True, blank=True)  # 리그 종료일 (자동 계산)

    participants = models.ManyToManyField(Team, related_name="leagues")  # 참가 팀

    def __str__(self):
        return self.league_name

    @property
    def total_matches(self):
        """
        리그 내 총 경기 수 계산 (모든 팀이 각 라운드에서 상대 팀과 몇 번 대결하는지에 따라).
        """
        num_teams = self.participants.count()
        return (num_teams * (num_teams - 1)) // 2 * self.total_number_of_rounds

    def generate_schedule(self):
        """
        각 팀이 각 라운드에서 상대팀과 경기할 수 있도록 매치 스케줄을 생성.
        라운드마다 모든 팀이 다른 팀과 한 번씩 대결함.
        """
        teams = list(self.participants.all())
        num_teams = len(teams)
        
        matches_per_round = []
        
        for round_number in range(1, self.total_number_of_rounds + 1):
            round_matches = []
            for i in range(0, num_teams - 1, 2):
                home_team = teams[i]
                away_team = teams[i + 1]
                # 여기서 매치와 관련된 로직을 추가하여 각 라운드에 팀들을 배치
                round_matches.append((home_team, away_team))
            matches_per_round.append(round_matches)
            teams = [teams[0]] + teams[2:] + teams[1:2]  # 로테이션 방식으로 팀 섞기

        return matches_per_round
    
    scheduling_type = models.CharField(max_length=50, choices=SCHEDULING_TYPES, default='organizer_based')  # 스케줄링 타입
    deadline = models.DateField(null=True, blank=True)  # 마감일 (마감일 기반 스케줄링 시)
    
    def __str__(self):
        return f"{self.league_name} organized by {self.organizer.username}"

# League_Status 모델
class LeagueStatus(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # 팀과 연결
    current_position = models.IntegerField()  # 현재 순위
    final_position = models.IntegerField(null=True, blank=True)  # 최종 순위
    league_points = models.IntegerField(default=0)  # 리그 점수
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    points_scored = models.IntegerField(default=0)  # 득점
    points_conceded = models.IntegerField(default=0)  # 실점
    matches_played = models.IntegerField(default=0)  # 경기 수

    def __str__(self):
        return f"{self.team.name} in {self.league.league_name} (Position: {self.current_position})"



