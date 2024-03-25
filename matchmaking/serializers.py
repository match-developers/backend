from rest_framework import serializers

from .models import Match, MatchPost, MatchScore


class MatchScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchScore
        fields = [
            "home_score",
            "away_score",
        ]


class MatchPostContentSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "sports_ground",
            "sport",
            "score",
            "creator",
            "start_time",
            "duration",
            "is_public",
            "is_club",
            "average_level",
            "home",
            "away",
            "status",
            "match_type",
            "participants",
        ]

    def get_score(self, obj):
        if obj.score:
            return MatchScoreSerializer(obj.score).data
        return None


class MatchPostSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likes.count")

    class Meta:
        model = MatchPost
        fields = ("title", "user", "likes", "match")
