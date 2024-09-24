from rest_framework import serializers
from .models.match import Match, MatchEvent, PressConference, TeamTalk, PlayerReview, GroundReview
from .models.team import Team, TeamPlayer
from newsfeed.models.newsfeed import NewsfeedPost
from newsfeed.models.match_post import MatchPost


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'club', 'is_red_team']


class TeamPlayerSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = TeamPlayer
        fields = ['id', 'team', 'user', 'is_starting_player']

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "profile_picture": obj.user.profile.profile_picture.url if obj.user.profile.profile_picture else None
        }


class MatchSerializer(serializers.ModelSerializer):
    participants = TeamPlayerSerializer(many=True)
    league = serializers.StringRelatedField()  # Optional: add related league information
    tournament = serializers.StringRelatedField()  # Optional: add related tournament information

    class Meta:
        model = Match
        fields = ['sports_ground', 'facility', 'price', 'start_time', 'duration', 'match_type', 'total_spots', 'league', 'tournament', 'winning_method', 'status', 'participants']

    def create(self, validated_data):
        """
        매치 생성 로직을 처리하는 메소드.
        매치 생성 시 뉴스피드 포스트 생성 추가.
        """
        match = Match.objects.create(**validated_data)
        # 매치 생성 시 뉴스피드 포스트 생성
        match.create_match_post()
        return match

    def update(self, instance, validated_data):
        """
        매치 수정 로직을 처리하는 메소드.
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
    participants = TeamPlayerSerializer(many=True)

    class Meta:
        model = Match
        fields = ['is_private', 'participants', 'join_requests']


class MatchEventSerializer(serializers.ModelSerializer):
    added_by = TeamPlayerSerializer()
    target_player = TeamPlayerSerializer()

    class Meta:
        model = MatchEvent
        fields = ['event_type', 'timestamp', 'added_by', 'target_player']

    def create(self, validated_data):
        return MatchEvent.objects.create(**validated_data)


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
    reviewer = serializers.SerializerMethodField()
    player = serializers.SerializerMethodField()

    class Meta:
        model = PlayerReview
        fields = ['reviewer', 'player', 'manner', 'performance', 'written_review']

    def get_reviewer(self, obj):
        return {
            "id": obj.reviewer.id,
            "username": obj.reviewer.username,
        }

    def get_player(self, obj):
        return {
            "id": obj.player.id,
            "username": obj.player.username,
        }


class GroundReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()
    ground = serializers.SerializerMethodField()

    class Meta:
        model = GroundReview
        fields = ['reviewer', 'ground', 'quality', 'safety', 'support', 'written_review']

    def get_reviewer(self, obj):
        return {
            "id": obj.reviewer.id,
            "username": obj.reviewer.username,
        }

    def get_ground(self, obj):
        return {
            "id": obj.ground.id,
            "name": obj.ground.name,
        }


# 추가된 뉴스피드와 관련된 메소드 처리
class MatchPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPost
        fields = ['match', 'created_by', 'post_content', 'created_at']
    
    def create(self, validated_data):
        match_post = MatchPost.objects.create(**validated_data)
        # 뉴스피드 포스트 생성 로직 추가
        NewsfeedPost.objects.create(
            newsfeed=match_post.created_by.newsfeed,
            post_type="match",
            post_id=match_post.id
        )
        return match_post