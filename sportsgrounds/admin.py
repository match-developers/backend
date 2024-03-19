from django.contrib.gis import admin

from .models import SportGround

admin.site.register(SportGround, admin.OSMGeoAdmin)
