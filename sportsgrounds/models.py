from django.contrib.gis.db import models

from model_utils.models import TimeStampedModel


class SportGround(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()
    description = models.TextField(blank=True, null=True)


class SportGroundGallery(TimeStampedModel):
    image = models.ImageField(upload_to="sportsgrounds/gallery/")
    description = models.TextField()
    sportground = models.ForeignKey(
        SportGround, related_name="gallery", on_delete=models.CASCADE
    )
