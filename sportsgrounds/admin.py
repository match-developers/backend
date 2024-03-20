from django.contrib.gis import admin

from .models import SportGround, SportGroundGallery

admin.site.register(SportGround, admin.OSMGeoAdmin)
admin.site.register(SportGroundGallery)
