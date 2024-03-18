from rest_framework import serializers

from .models import Match


class MatchPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            "sports_ground",
            "sport",
            "matchscore",
            "home_club",
            "away_club",
            "start_time",
            "duration",
            "is_public",
            "is_club",
            "average_level",
            "status",
            "match_type",
        ]
