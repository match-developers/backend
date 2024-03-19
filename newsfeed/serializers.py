from django.db.models import Count

from rest_framework import serializers

from matchmaking.serializers import MatchPostContentSerializer

from .models import Comment, CustomPost


class CustomPostSerializer(serializers.ModelSerializer):
    # TODO
    pass


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
