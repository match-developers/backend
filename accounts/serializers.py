from rest_framework import serializers
from django.contrib.auth import authenticate

from newsfeed.models.newsfeed import NewsfeedPost
from .models.users import User, UserStatistics, PlaystyleTest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'profile_photo', 'bio']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid login credentials.")

class SocialLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    provider = serializers.CharField()
    social_id = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data['email'], provider=data['provider'], social_id=data['social_id']).first()
        if user:
            return user
        raise serializers.ValidationError("Invalid social login credentials.")
    
class NewsfeedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsfeedPost
        fields = ['id', 'post_type', 'post_content', 'created_at']
        
class UserStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistics
        fields = ['mp', 'wins', 'draws', 'losses', 'points_scored', 'manner', 'performance', 
                  'current_club', 'previous_clubs', 'current_league', 'current_tournament', 'playstyle']
        
class PlaystyleTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaystyleTest
        fields = ['questions', 'result', 'taken_at']
        
        
class FollowUserSerializer(serializers.ModelSerializer):
    """
    유저의 팔로우/팔로잉 정보를 직렬화하는 시리얼라이저.
    """
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_photo', 'bio', 'followers_count', 'following_count', 'is_following']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        # 현재 요청한 유저가 해당 유저를 팔로우하고 있는지 확인
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.followers.filter(id=request.user.id).exists()
        return False