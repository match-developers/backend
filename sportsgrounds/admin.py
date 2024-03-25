from django.contrib.gis import admin

from .models import SportGround, SportGroundGallery


class SportGroundGalleryInline(admin.StackedInline):
    model = SportGroundGallery
    extra = 1  # Number of extra forms to display


class SportGroundAdmin(admin.OSMGeoAdmin):
    inlines = [SportGroundGalleryInline]


admin.site.register(SportGround, SportGroundAdmin)
