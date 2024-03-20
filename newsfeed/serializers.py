from django.db.models import Count

from rest_framework import serializers

from matchmaking.serializers import MatchPostContentSerializer

from .models import Comment, CustomPost


class CustomPostSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likes.count")

    class Meta:
        model = CustomPost
        fields = ("title", "user", "likes", "content_object")
        depth = 1


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
