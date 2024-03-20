from django.contrib import admin

from .models import Club, ClubGallery


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "user_name")
    search_fields = ("name", "user_name")


admin.site.register(ClubGallery)
