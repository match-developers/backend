from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.gis.db import models as gis_models
from .managers import CustomUserManager

from clubs.models.clubs import Club
from sportsgrounds.models.sports_ground import SportsGround  # 스포츠 그라운드 모델 추가
from leagues.models.league import League
from tournaments.models.tournament import Tournament
from matchmaking.models.match import PlayerReview
from newsfeed.models.newsfeed import NewsfeedPost


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(("User Name"), max_length=150)
    first_name = models.CharField(("First Name"), max_length=150)
    last_name = models.CharField(("Last Name"), max_length=150)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # 클럽 소유자 정보
    owned_clubs = models.ManyToManyField(Club, related_name="owned_club", blank=True)
    
    # 스포츠 그라운드 소유자 정보
    owned_sports_grounds = models.ManyToManyField(SportsGround, related_name="owned_ground", blank=True)
    
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

    def is_club_owner(self, club):
        """
        사용자가 해당 클럽의 소유자인지 확인.
        """
        return club in self.owned_clubs.all()

    def is_sports_ground_owner(self, sports_ground):
        """
        사용자가 해당 스포츠 그라운드의 소유자인지 확인.
        """
        return sports_ground in self.owned_sports_grounds.all()


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
    
class PlaystyleTest(models.Model):
    user_statistics = models.ForeignKey(UserStatistics, on_delete=models.CASCADE)
    questions = models.JSONField()
    result = models.CharField(max_length=255)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_statistics.user.username}'s Playstyle Test Result: {self.result}"