from django.db.models import Count

from rest_framework import serializers

from matchmaking.serializers import MatchPostSerializer

from .models import ClubPost, Comment, IndividualPost, Like


class ClubPostSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    match = MatchPostSerializer()

    def get_like_count(self, obj):
        return obj.likes_count

    class Meta:
        model = ClubPost
        fields = ("title", "user", "like_count", "match")

    def to_representation(self, instance):
        self.fields["like_count"] = serializers.IntegerField(read_only=True)
        return super().to_representation(instance)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(likes_count=Count("likes"))
        return queryset


class IndividualPostSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    match = MatchPostSerializer()

    def get_like_count(self, obj):
        return obj.likes_count

    class Meta:
        model = IndividualPost
        fields = ("title", "user", "like_count", "match")

    def to_representation(self, instance):
        self.fields["like_count"] = serializers.IntegerField(read_only=True)
        return super().to_representation(instance)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(likes_count=Count("likes"))
        return queryset


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
