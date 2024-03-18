from django.db.models import Count

from rest_framework import serializers

from .models import ClubPost, IndividualPost, Like


class ClubPostSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.likes_count

    class Meta:
        model = ClubPost
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["like_count"] = serializers.IntegerField(read_only=True)
        return super().to_representation(instance)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(likes_count=Count("likes"))
        return queryset


class IndividualPostSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.likes_count

    class Meta:
        model = IndividualPost
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["like_count"] = serializers.IntegerField(read_only=True)
        return super().to_representation(instance)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(likes_count=Count("likes"))
        return queryset
