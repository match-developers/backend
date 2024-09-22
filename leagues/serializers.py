from rest_framework import serializers
from leagues.models.league import League, LeagueStatus
from leagues.models.league_match import LeagueMatch
from matchmaking.models.team import Team

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']

class LeagueSerializer(serializers.ModelSerializer):
    participants = TeamSerializer(many=True, read_only=True)  # 팀 정보 포함

    class Meta:
        model = League
        fields = ['id', 'league_name', 'description', 'league_type', 'participants', 'total_number_of_rounds', 
                  'current_round', 'start_date', 'deadline', 'max_teams', 'organizer', 'scheduling_type']

class LeagueStatusSerializer(serializers.ModelSerializer):
    team = TeamSerializer()  # 팀 정보 포함

    class Meta:
        model = LeagueStatus
        fields = ['league', 'team', 'current_position', 'league_points', 'wins', 'draws', 'losses', 'matches_played']

class LeagueMatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer()
    away_team = TeamSerializer()

    class Meta:
        model = LeagueMatch
        fields = ['league', 'match', 'home_team', 'away_team', 'round_number', 'match_date', 'match_time']