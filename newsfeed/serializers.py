from rest_framework import serializers

from .models import Comment, CustomPost


class CustomPostRetrieveSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likes.count")

    class Meta:
        model = CustomPost
        fields = ("title", "user", "likes", "content_object")
        depth = 1


class CustomPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPost
        fields = ("title", "user", "content_object", "object_id")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
