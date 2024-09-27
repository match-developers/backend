from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models

# User, Match는 문자열로 참조
from matchmaking.models.team import Team  # Team 모델 임포트
from newsfeed.models.newsfeed import NewsfeedPost
from newsfeed.models.league_post import LeaguePost


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
    
    organizer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)  # 문자열 참조
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
            participants = list(models.get_model('accounts', 'User').objects.filter(user_statistics__current_league=self))
            num_participants = len(participants)
            if num_participants % 2 != 0:
                return []
            
            for i in range(0, num_participants, 2):
                team_1 = Team.objects.create(name=f"Team {i+1}")
                team_2 = Team.objects.create(name=f"Team {i+2}")
                self.participants.add(team_1, team_2)
                team_1.players.add(participants[i])
                team_2.players.add(participants[i + 1])

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
                match = models.get_model('matchmaking', 'Match').objects.create(
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
    
    def create_league_post(self):
        """
        리그 생성 시, 뉴스피드에 포스트를 생성하는 메서드.
        """
        # 뉴스피드 포스트 생성
        newsfeed_post = NewsfeedPost.objects.create(
            newsfeed=self.organizer.newsfeed,  # 리그 주최자의 뉴스피드에 추가
            post_type="league",
            post_id=self.id,
            post_content=f"League {self.league_name} has been created! Join now!"
        )

        # 리그 포스트 생성
        LeaguePost.objects.create(
            league=self,
            created_by=self.organizer,
            post_content=f"League {self.league_name} has been created!",
            newsfeed_post=newsfeed_post
        )

### 2. 참가 인원이 꽉 찼을 때 포스트 업데이트
    def update_league_post_on_full_participation(self):
        """
        리그 참가 인원이 꽉 찼을 때 뉴스피드 포스트 업데이트
        """
        if self.participants.count() >= self.max_teams:  # 모든 팀이 참여했을 때
            newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="league")
            newsfeed_post.post_content = f"League {self.league_name} is now full! The games will begin soon."
            newsfeed_post.save()

### 3. 라운드 완료 후 포스트 업데이트
    def update_league_post_on_round_completion(self):
        """
        각 라운드가 완료되었을 때 뉴스피드 포스트 업데이트
        """
        newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="league")
        newsfeed_post.post_content = f"Round {self.current_round} of League {self.league_name} is now complete!"
        newsfeed_post.save()

### 4. 리그 종료 시 최종 포스트 업데이트
    def update_league_post_on_completion(self):
        """
        리그가 완료되었을 때 최종 결과를 뉴스피드 포스트로 업데이트
        """
        newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="league")
        newsfeed_post.post_content = f"League {self.league_name} has been completed! Congratulations to the winners!"
        newsfeed_post.save()


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