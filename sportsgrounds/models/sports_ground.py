from django.contrib.gis.db import models
from model_utils.models import TimeStampedModel
from matchmaking.models.match import GroundReview  # 리뷰 모델 가져오기
from accounts.models.users import User


class SportsGround(models.Model):
    name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='sportsgrounds/photos/', null=True, blank=True)  # 프로필 사진
    location = models.PointField()  # 위치
    description = models.TextField(blank=True, null=True)  # 설명
    support = models.TextField(blank=True, null=True)  # 시설 지원 정보
    rules = models.TextField(blank=True, null=True)  # 규칙
    opening_hours = models.TextField(blank=True, null=True)  # 개장 시간 정보
    average_rating = models.ManyToManyField(GroundReview, related_name='groundratings', blank=True)  # 평균 평점
    reviews = models.ManyToManyField(GroundReview.written_review, related_name='groundreviews', blank=True)  # 리뷰 (다대다 관계)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_grounds")  # 소유자 필드 추가

    def __str__(self):
        return self.name