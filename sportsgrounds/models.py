from django.contrib.gis.db import models


class SportGround(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()
