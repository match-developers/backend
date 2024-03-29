from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
    Comment,
    CustomPost,
    ImageAttachment,
    TextAttachment,
    VideoAttachment,
)


class TextAttachmentInline(GenericTabularInline):
    model = TextAttachment


class VideoAttachmentInline(GenericTabularInline):
    model = VideoAttachment


class ImageAttachmentInline(GenericTabularInline):
    model = ImageAttachment


class CustomPostAdmin(admin.ModelAdmin):
    inlines = [TextAttachmentInline, VideoAttachmentInline, ImageAttachmentInline]
    list_display = ("id", "title")


admin.site.register(CustomPost, CustomPostAdmin)
admin.site.register(Comment)
