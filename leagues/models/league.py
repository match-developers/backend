from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from accounts.models.users import User, UserStatistics
from matchmaking.models.match import Match
from matchmaking.models.team import Team, TeamPlayer

# League 모델
class League(models.Model):
    LEAGUE_TYPES = [
        ('club', 'Club'),
        ('individual', 'Individual'),
    ]
    
    SCHEDULING_TYPES = [
        ('organizer_based', 'Organizer Based'),
        ('deadline_based', 'Deadline Based'),
    ]
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    league_name = models.CharField(max_length=255)
    description = models.TextField()
    league_type = models.CharField(max_length=50, choices=LEAGUE_TYPES, default='individual')
    participants = models.ManyToManyField(Team, related_name="leagues")
    
    # 추가 필드
    total_number_of_rounds = models.IntegerField()  # 총 라운드 수
    max_teams = models.IntegerField()  # 팀 수
    start_date = models.DateField()  # 리그 시작일
    deadline = models.DateField()  # 전체 리그 마감일
    current_round = models.IntegerField(default=1)
    scheduling_type = models.CharField(max_length=50, choices=SCHEDULING_TYPES, default='organizer_based')
    
    # 매치 관련 필드
    match_duration = models.DurationField()  # 매치 경기 시간
    winning_method = models.CharField(max_length=255)  # 승리 조건

    def __str__(self):
        return self.league_name

    def generate_teams(self):
        """
        개인 리그일 경우 참가자를 팀으로 자동 생성.
        """
        if self.league_type == 'individual':
            participants = list(UserStatistics.objects.filter(current_league=self))
            num_participants = len(participants)
            if num_participants % 2 != 0:
                return []
            
            team_size = num_participants // 2
            for i in range(0, num_participants, 2):
                team_1 = Team.objects.create(name=f"Team {i+1}")
                team_2 = Team.objects.create(name=f"Team {i+2}")
                self.participants.add(team_1, team_2)
                team_1.players.add(participants[i].user)
                team_2.players.add(participants[i + 1].user)

    def generate_schedule(self):
        """
        리그 매치 생성 메서드. 스케줄링은 시간과 장소 없이 매치만 생성.
        """
        teams = list(self.participants.all())
        num_teams = len(teams)
        if num_teams != self.max_teams:
            return []
        
        matches_per_round = []
        for round_number in range(1, self.total_number_of_rounds + 1):
            round_matches = []
            for i in range(0, num_teams - 1, 2):
                home_team = teams[i]
                away_team = teams[i + 1]
                match = Match.objects.create(
                    home_team=home_team,
                    away_team=away_team,
                    match_type='league',
                    status='scheduled',
                    duration=self.match_duration,
                    winning_method=self.winning_method
                )
                round_matches.append(match)
            matches_per_round.append(round_matches)
            teams = [teams[0]] + teams[2:] + teams[1:2]
        return matches_per_round

    def validate_join(self, user):
        """
        리그 시작일 이후 참가 차단.
        """
        if self.start_date < timezone.now().date():
            raise ValidationError("You cannot join this league after it has started.")
        
        if self.participants.count() >= self.max_teams:
            raise ValidationError("This league is full.")

        return True

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



