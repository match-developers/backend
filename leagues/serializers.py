from rest_framework import serializers
from leagues.models.league import League, LeagueStatus
from leagues.models.league_match import LeagueMatch
from matchmaking.models.team import Team
from newsfeed.models.league_post import LeaguePost  # 뉴스피드 관련 모델 추가

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

    def create(self, validated_data):
        """
        리그 생성 시, 자동으로 LeaguePost를 생성하여 뉴스피드에 반영.
        """
        league = super().create(validated_data)
        league.create_league_post()  # 리그 생성 시 뉴스피드에 포스트 추가
        return league

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

class LeaguePostSerializer(serializers.ModelSerializer):
    """
    LeaguePost 모델에 대한 시리얼라이저. 리그 관련 뉴스피드 포스트에 사용.
    """
    class Meta:
        model = LeaguePost
        fields = ['league', 'created_by', 'post_content', 'created_at']