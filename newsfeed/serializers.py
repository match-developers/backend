from rest_framework import serializers

from .models import ClubPost, IndividualPost


class ClubPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubPost
        fields = "__all__"


class IndividualPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualPost
        fields = "__all__"
