from model_utils.models import TimeStampedModel
from django.db import models
from accounts.models import User
from matchmaking.models import WinningMethod, Team

class Tournament(TimeStampedModel):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)  # 토너먼트 주최자
    tournament_name = models.CharField(max_length=255)
    description = models.TextField()

    # 승리 조건 및 경기 정보
    winning_method = models.ForeignKey(WinningMethod, on_delete=models.SET_NULL, null=True, blank=True)
    match_duration = models.DurationField()  # 각 매치의 경기 시간
    
    # 참가 팀 및 라운드 관련 정보
    participants = models.ManyToManyField(Team, related_name="tournaments")
    total_number_of_rounds = models.IntegerField()  # 총 라운드 수
    current_round = models.IntegerField(default=1)  # 현재 진행 중인 라운드
    start_date = models.DateField()  # 토너먼트 시작일
    end_date = models.DateField(null=True, blank=True)  # 토너먼트 종료일 (자동 계산)

    def __str__(self):
        return f"{self.tournament_name} organized by {self.organizer.username}"

    @property
    def total_matches(self):
        """
        토너먼트 내 총 경기 수 계산 (모든 팀이 각 라운드에서 상대 팀과 대결).
        """
        num_teams = self.participants.count()
        return (num_teams - 1) * self.total_number_of_rounds

    def generate_bracket(self):
        """
        토너먼트 대진표를 생성하는 메서드.
        각 라운드에서 팀이 상호 대결할 수 있도록 매치 스케줄을 생성함.
        """
        teams = list(self.participants.all())
        num_teams = len(teams)
        
        bracket = []
        round_number = 1
        
        while len(teams) > 1:
            round_matches = []
            for i in range(0, num_teams - 1, 2):
                home_team = teams[i]
                away_team = teams[i + 1]
                # 여기서 각 라운드의 매치들을 생성
                round_matches.append((home_team, away_team))
            bracket.append(round_matches)
            teams = teams[:num_teams // 2]  # 다음 라운드를 위해 팀을 절반으로 줄임
            round_number += 1

        return bracket

    def advance_round(self):
        """
        토너먼트 라운드를 진행하는 메서드.
        다음 라운드로 진출.
        """
        if self.current_round < self.total_number_of_rounds:
            self.current_round += 1
        else:
            self.current_round = self.total_number_of_rounds  # 마지막 라운드 유지

class TournamentStatus(TimeStampedModel):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)  # 토너먼트와 연결
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # 팀과 연결
    current_round = models.IntegerField(default=1)  # 현재 라운드
    advancement_status = models.CharField(max_length=50, choices=[
        ('in_progress', 'In Progress'),
        ('eliminated', 'Eliminated'),
        ('completed', 'Completed')
    ], default='in_progress')  # 진행 상태 (진행 중, 탈락, 완료)
    wins = models.IntegerField(default=0)  # 승리 횟수
    losses = models.IntegerField(default=0)  # 패배 횟수
    matches_played = models.IntegerField(default=0)  # 플레이한 경기 수
    final_position = models.IntegerField(null=True, blank=True)  # 최종 순위 (선택 사항)

    def __str__(self):
        return f"Team {self.team.name} in {self.tournament.tournament_name} - Round {self.current_round}"

    def update_status(self, win=False):
        """
        경기 결과에 따라 팀의 상태를 업데이트하는 메서드.
        """
        self.matches_played += 1
        if win:
            self.wins += 1
        else:
            self.losses += 1
        # 토너먼트에서 탈락 여부 확인
        if self.losses >= 2:  # 예시로 이중 엘리미네이션 조건 (패배 2번 탈락)
            self.advancement_status = 'eliminated'
        self.save()