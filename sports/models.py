from django.db import models

from .choices import SPORT_CHOICES


class SportPosition(models.Model):
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    position_name = models.CharField(max_length=50)

    def __str__(self):
        return self.position_name
