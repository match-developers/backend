from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from newsfeed.models.newsfeed import NewsfeedPost
from .models.users import User, UserStatistics, PlaystyleTest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'profile_photo', 'bio', 'location']

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
    user_statistics = serializers.PrimaryKeyRelatedField(
        queryset=UserStatistics.objects.all(), required=True
    )  # 유저 통계와 연결

    class Meta:
        model = PlaystyleTest
        fields = ['user_statistics', 'questions', 'result', 'taken_at']
        read_only_fields = ['taken_at']  # `taken_at` 필드는 읽기 전용

    def create(self, validated_data):
        """
        플레이스타일 테스트 생성 또는 업데이트 로직.
        """
        user_statistics = validated_data.get('user_statistics')

        # 해당 유저의 PlaystyleTest 인스턴스가 이미 있는지 확인
        playstyle_test, created = PlaystyleTest.objects.update_or_create(
            user_statistics=user_statistics,
            defaults={
                'questions': validated_data.get('questions'),
                'result': validated_data.get('result')
            }
        )
        return playstyle_test
        
        
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
    
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)  # 장고 기본 비밀번호 검증 사용
        return value

    def validate(self, data):
        user = self.context['request'].user

        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Incorrect old password."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user