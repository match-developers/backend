from rest_framework import serializers
from accounts.models.users import User
from clubs.models.clubs import Club
from clubs.models.club_statistics import ClubStatistics
from clubs.models.tactics import Tactic

### 1. 클럽 기본 정보 시리얼라이저
class ClubSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    member_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Club
        fields = ['id', 'name', 'profile_photo', 'bio', 'member_number', 'followers', 'owner']

### 2. 클럽 통계 정보 시리얼라이저
class ClubStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubStatistics
        fields = ['mp', 'wins', 'draws', 'losses', 'points_scored', 'manner', 'performance', 'reviews', 'playstyle']

### 3. 클럽 멤버 정보 시리얼라이저
class ClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_photo', 'first_name', 'last_name']

### 4. 택틱 시리얼라이저
class TacticSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tactic
        fields = ['id', 'tactic_explanation', 'created_by', 'created_at', 'updated_at']

### 5. 라인업 시리얼라이저
class LineupSerializer(serializers.Serializer):
    starters = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True
    )
    substitutes = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True
    )
    formation = serializers.JSONField()

    class Meta:
        fields = ['starters', 'substitutes', 'formation']

### 6. 권한 관리 시리얼라이저
class PermissionSerializer(serializers.Serializer):
    permission_type = serializers.ChoiceField(choices=['create_match', 'manage_team', 'assign_owner', 'manage_requests'])

    class Meta:
        fields = ['permission_type']