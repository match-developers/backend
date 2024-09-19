from rest_framework import serializers
from .models.match import Match, MatchEvent, PressConference, TeamTalk, PlayerReview, GroundReview
from .models.team import TeamPlayer

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['sports_ground', 'facility', 'price', 'start_time', 'duration', 'match_type', 'total_spots', 'league', 'tournament', 'winning_method', 'status']

    def create(self, validated_data):
        """
        매치 생성 로직을 처리하는 메소드
        """
        return Match.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        매치 수정 로직을 처리하는 메소드
        """
        instance.sports_ground = validated_data.get('sports_ground', instance.sports_ground)
        instance.facility = validated_data.get('facility', instance.facility)
        instance.price = validated_data.get('price', instance.price)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.total_spots = validated_data.get('total_spots', instance.total_spots)
        instance.status = validated_data.get('status', instance.status)
        instance.match_type = validated_data.get('match_type', instance.match_type)
        
        instance.save()
        return instance

class MatchJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['is_private', 'participants', 'join_requests']
        
class MatchEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchEvent
        fields = ['event_type', 'timestamp', 'added_by', 'target_player']

    def create(self, validated_data):
        return MatchEvent.objects.create(**validated_data)
    
class TeamPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamPlayer
        fields = ['id', 'team', 'user', 'is_starting_player']
        
class PressConferenceSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = PressConference
        fields = ['match', 'participants', 'questions', 'chat_log', 'current_question_index']
        
class TeamTalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamTalk
        fields = ['chat_log', 'team', 'match']
        
class PlayerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerReview
        fields = ['manner', 'performance', 'written_review']

class GroundReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundReview
        fields = ['quality', 'safety', 'support', 'written_review']