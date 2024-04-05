from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html

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
    readonly_fields = ("display_video",)

    def display_video(self, obj):
        return format_html(
            '<video width="320" height="240" controls><source src="{}" type="video/mp4"></video>',
            obj.video.url,
        )

    display_video.short_description = "Video"


class ImageAttachmentInline(GenericTabularInline):
    model = ImageAttachment
    readonly_fields = ("display_image",)

    def display_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.image.url)

    display_image.short_description = "Image"


class CustomPostAdmin(admin.ModelAdmin):
    inlines = [TextAttachmentInline, VideoAttachmentInline, ImageAttachmentInline]
    list_display = ("id", "title")


admin.site.register(CustomPost, CustomPostAdmin)
admin.site.register(Comment)
