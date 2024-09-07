from django.contrib.gis.db import models

from model_utils.models import TimeStampedModel


class SportGround(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name