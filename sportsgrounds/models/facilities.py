from django.contrib.gis.db import models

from model_utils.models import TimeStampedModel

from . import SportGround

class SportGroundGallery(TimeStampedModel):
    image = models.ImageField(upload_to="sportsgrounds/gallery/")
    description = models.TextField(blank=True, null=True)
    sportground = models.ForeignKey(
        SportGround, related_name="gallery", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.sportground} gallery"
