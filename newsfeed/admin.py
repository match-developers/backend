from django.contrib import admin

from .models import Comment, CustomPost

admin.site.register(CustomPost)
admin.site.register(Comment)
