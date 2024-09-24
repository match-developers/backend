from rest_framework import serializers
from newsfeed.models.newsfeed import Newsfeed, NewsfeedPost
from newsfeed.models.match_post import MatchPost
from newsfeed.models.league_post import LeaguePost
from newsfeed.models.tournament_post import TournamentPost
from newsfeed.models.transfer_post import TransferPost

class NewsfeedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsfeedPost
        fields = ['id', 'newsfeed', 'post_type', 'post_id', 'created_at', 'likes', 'comments', 'shares']

class MatchPostSerializer(serializers.ModelSerializer):
    newsfeed_post = NewsfeedPostSerializer()

    class Meta:
        model = MatchPost
        fields = ['id', 'match', 'created_by', 'post_content', 'created_at', 'newsfeed_post']

class LeaguePostSerializer(serializers.ModelSerializer):
    newsfeed_post = NewsfeedPostSerializer()

    class Meta:
        model = LeaguePost
        fields = ['id', 'league', 'created_by', 'post_content', 'created_at', 'newsfeed_post']

class TournamentPostSerializer(serializers.ModelSerializer):
    newsfeed_post = NewsfeedPostSerializer()

    class Meta:
        model = TournamentPost
        fields = ['id', 'tournament', 'created_by', 'post_content', 'created_at', 'newsfeed_post']

class TransferPostSerializer(serializers.ModelSerializer):
    newsfeed_post = NewsfeedPostSerializer()

    class Meta:
        model = TransferPost
        fields = ['id', 'user', 'club', 'transfer_type', 'created_at', 'newsfeed_post']