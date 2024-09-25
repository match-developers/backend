from rest_framework import serializers
from tournaments.models.tournament import Tournament, TournamentStatus
from tournaments.models.tournament_match import TournamentMatch
from matchmaking.models.team import Team
from matchmaking.serializers import TeamSerializer

class TournamentSerializer(serializers.ModelSerializer):
    participants = TeamSerializer(many=True, read_only=True)  # 팀 정보 포함
    
    class Meta:
        model = Tournament
        fields = ['id', 'tournament_name', 'description', 'tournament_type', 'participants', 
                  'total_number_of_rounds', 'current_round', 'start_date', 'deadline', 
                  'max_teams', 'match_duration', 'winning_method']
    
    def create(self, validated_data):
        """
        토너먼트 생성 시 처리
        """
        tournament = Tournament.objects.create(**validated_data)
        tournament.create_tournament_post()  # 토너먼트 생성 시 포스트 생성
        return tournament

class TournamentStatusSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TournamentStatus
        fields = ['tournament', 'team', 'current_round', 'advancement_status', 
                  'wins', 'losses', 'matches_played', 'final_position']

class TournamentMatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer()
    away_team = TeamSerializer()

    class Meta:
        model = TournamentMatch
        fields = ['tournament', 'match', 'home_team', 'away_team', 'round_number', 'is_knockout_stage']

    def update(self, instance, validated_data):
        """
        토너먼트 매치 상태 업데이트
        """
        instance.home_team = validated_data.get('home_team', instance.home_team)
        instance.away_team = validated_data.get('away_team', instance.away_team)
        instance.round_number = validated_data.get('round_number', instance.round_number)
        instance.is_knockout_stage = validated_data.get('is_knockout_stage', instance.is_knockout_stage)
        instance.save()
        
        # 라운드 완료 시 뉴스피드 포스트 업데이트
        tournament = instance.tournament
        tournament.update_tournament_post_on_round_completion()

        return instance