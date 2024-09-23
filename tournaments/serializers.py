from rest_framework import serializers
from tournaments.models.tournament import Tournament, TournamentStatus
from tournaments.models.tournament_match import TournamentMatch
from matchmaking.models.team import Team
from matchmaking.serializers import TeamSerializer

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'tournament_name', 'description', 'tournament_type', 'participants', 
                  'total_number_of_rounds', 'current_round', 'start_date', 'deadline', 
                  'max_teams', 'match_duration', 'winning_method']

class TournamentStatusSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TournamentStatus
        fields = ['tournament', 'team', 'current_round', 'advancement_status', 
                  'wins', 'losses', 'matches_played', 'final_position']

class TournamentMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentMatch
        fields = ['tournament', 'match', 'home_team', 'away_team', 'round_number', 'is_knockout_stage']