from django.contrib.gis.db import models
from model_utils.models import TimeStampedModel
from . import SportsGround
from matchmaking.models import Match  # Match 모델을 import

class Facilities(models.Model):
    sports_ground = models.ForeignKey(SportsGround, on_delete=models.CASCADE, related_name='facilities')
    facility_name = models.CharField(max_length=255)
    facility_description = models.TextField()
    facility_price = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.ImageField(upload_to='facilities/photos/', null=True, blank=True)
    
    def available_times(self):
        # 예약된 시간을 Match 모델과 상호작용하여 계산
        matches = Match.objects.filter(facility=self)
        reserved_times = [(match.date, match.time) for match in matches]  # 이미 예약된 시간대
        # 로직을 통해 사용 가능한 시간대를 계산해서 반환
        # 예시: 모든 가능한 시간대에서 reserved_times를 제외한 시간대 반환
        return reserved_times

    def __str__(self):
        return self.facility_name