from django.contrib import admin

from .models import Comment, Like, MatchPost

admin.site.register(MatchPost)
admin.site.register(Comment)
