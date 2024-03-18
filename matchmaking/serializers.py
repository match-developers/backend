from rest_framework import serializers

from .models import Match, MatchScore


class MatchPostContentSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "sports_ground",
            "sport",
            "score",
            "home",
            "away",
            "start_time",
            "duration",
            "is_public",
            "is_club",
            "average_level",
            "status",
            "match_type",
        ]

    def get_score(self, obj):
        if obj.score:
            return MatchScoreSerializer(obj.score).data
        return None


class MatchScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchScore
        fields = [
            "home_score",
            "away_score",
        ]
