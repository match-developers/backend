from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.gis.db import models as gis_models

from .managers import CustomUserManager
from clubs.models.clubs import Club
from leagues.models.league import League
from tournaments.models.tournament import Tournament
from matchmaking.models.match import MatchEvent, PlayerReview
from newsfeed.models.newsfeed import Newsfeed, NewsfeedPost


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(("User Name"), max_length=150)
    first_name = models.CharField(("First Name"), max_length=150)
    last_name = models.CharField(("Last Name"), max_length=150)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # 위치 정보 (위도, 경도 기반)
    location = gis_models.PointField(null=True, blank=True)
    
    # 소셜 로그인 관련 필드
    provider = models.CharField(max_length=50, null=True, blank=True)
    social_id = models.CharField(max_length=255, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    # 유저 프로필 뉴스피드: 유저가 직접 생성/참가한 매치, 리그, 토너먼트 포스트만 표시
    profile_newsfeed = models.OneToOneField(
        'newsfeed.Newsfeed', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='profile_newsfeed'
    )

    following = models.ManyToManyField(
        "self", 
        related_name="followers", 
        symmetrical=False
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name"]

    def __str__(self):
        return self.email

    def get_profile_newsfeed_posts(self):
        """
        유저가 생성/참가한 매치, 리그, 토너먼트와 관련된 뉴스피드 포스트만 필터링하여 반환
        """
        return NewsfeedPost.objects.filter(
            models.Q(creator=self) |  # 유저가 생성한 포스트
            models.Q(match__participants__user=self) |  # 유저가 참가한 매치 포스트
            models.Q(league__participants__user=self) |  # 유저가 참가한 리그 포스트
            models.Q(tournament__participants__user=self)  # 유저가 참가한 토너먼트 포스트
        ).distinct()


class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # User와 1:1 관계

    # 경기 관련 필드 (Match 모델과 연동)
    mp = models.IntegerField(default=0)  # 총 경기 수 (자동 계산)
    wins = models.IntegerField(default=0)  # 승리 수
    draws = models.IntegerField(default=0)  # 무승부 수
    losses = models.IntegerField(default=0)  # 패배 수
    points_scored = models.IntegerField(default=0)  # 득점

    # 매너, 성과, 리뷰
    manner = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 매너 점수 (0.00~5.00)
    performance = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 경기 성과 점수 (0.00~5.00)
    reviews = models.ForeignKey(PlayerReview, on_delete=models.CASCADE, null=True, blank=True)  # 리뷰

    # 클럽, 리그, 토너먼트 활동
    current_club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 클럽
    previous_clubs = models.ManyToManyField(Club, related_name="previous_clubs", blank=True)  # 이전 클럽 목록
    current_league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 리그
    current_tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 토너먼트

    # 플레이스타일 테스트 결과
    playstyle = models.CharField(max_length=255, blank=True, null=True)  # 플레이스타일

    def __str__(self):
        return f"{self.user.username} - Statistics"

    def update_match_stats(self, match_result, points):
        """
        경기 결과에 따라 유저의 경기 통계를 업데이트하는 메서드.
        match_result: 'win', 'draw', 'loss' 중 하나.
        points: 해당 경기에서 유저가 득점한 포인트.
        """
        self.mp += 1  # 총 경기 수 1 증가
        self.points_scored += points  # 득점 업데이트

        if match_result == 'win':
            self.wins += 1
        elif match_result == 'draw':
            self.draws += 1
        elif match_result == 'loss':
            self.losses += 1

        self.save()

    def update_performance_and_manner(self, performance_score, manner_score):
        """
        유저의 성과 및 매너 점수를 업데이트하는 메서드.
        performance_score: 경기 성과 점수 (0~5)
        manner_score: 매너 점수 (0~5)
        """
        self.performance = (self.performance * (self.mp - 1) + performance_score) / self.mp  # 성과 점수 평균 계산
        self.manner = (self.manner * (self.mp - 1) + manner_score) / self.mp  # 매너 점수 평균 계산
        self.save()

    def transfer_club(self, new_club):
        """
        유저가 클럽을 이동할 때 호출되는 메서드.
        """
        if self.current_club:
            self.previous_clubs.add(self.current_club)  # 이전 클럽 목록에 추가
        self.current_club = new_club  # 새로운 클럽 설정
        self.save()


class PlaystyleTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.JSONField()  # 테스트 질문
    result = models.CharField(max_length=255)  # 테스트 결과 저장
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Playstyle Test Result"