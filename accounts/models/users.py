from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

from . import User
from clubs.models import Club  # 클럽 모델
from leagues.models import League  # 리그 모델
from tournaments.models import Tournament  # 토너먼트 모델
from matchmaking.models.match import Match_Event, Review  # 매치, 리뷰 모델

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(_("User Name"), max_length=150)
    first_name = models.CharField(_("First Name"), max_length=150)
    last_name = models.CharField(_("last Name"), max_length=150)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # 소셜 로그인 관련 필드
    provider = models.CharField(max_length=50, null=True, blank=True)  # 소셜 로그인 제공자 (Google, Facebook 등)
    social_id = models.CharField(max_length=255, null=True, blank=True)  # 소셜 계정 ID
    is_email_verified = models.BooleanField(default=False)  # 이메일 인증 여부
    
    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name"]

    def __str__(self):
        return self.email

class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # User와 1:1 관계

    # 경기 관련 필드 (Match 모델과 연결)
    mp = models.IntegerField(default=0)  # 경기 수 (match event에서 가져온 데이터)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    points_scored = models.IntegerField(default=0)

    # 매너, 성과, 리뷰 (Review 모델과 연결)
    manner = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 매너 점수
    performance = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 성과 점수
    reviews = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True)  # 여러 리뷰

    # 클럽 및 대회 (Club, League, Tournament 모델과 연결)
    current_club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 클럽
    previous_clubs = models.ManyToManyField(Club, related_name="previous_clubs", blank=True)  # 이전 클럽들

    current_league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 리그
    current_tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)  # 현재 토너먼트

    playstyle = models.CharField(max_length=255, blank=True, null=True)  # 스포츠 플레이 스타일

    def __str__(self):
        return f"{self.user.username} - Statistics"