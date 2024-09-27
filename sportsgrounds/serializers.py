from rest_framework import serializers
from sportsgrounds.models.sports_ground import SportsGround, Booking
from sportsgrounds.models.facilities import Facilities, TimeSlot
from matchmaking.models.match import Match
from newsfeed.models.newsfeed import NewsfeedPost


class SportsGroundSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()  # 소유자의 정보를 간단하게 반환

    class Meta:
        model = SportsGround
        fields = ['id', 'name', 'profile_photo', 'location', 'description', 'support', 'rules', 'opening_hours', 'owner', 'average_rating']


class FacilitiesSerializer(serializers.ModelSerializer):
    sports_ground = serializers.StringRelatedField()  # 시설이 속한 스포츠 그라운드의 이름만 반환

    class Meta:
        model = Facilities
        fields = ['id', 'facility_name', 'facility_description', 'facility_price', 'photo_url', 'sports_ground']


class TimeSlotSerializer(serializers.ModelSerializer):
    facility = serializers.StringRelatedField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'facility', 'start_time', 'end_time', 'is_reserved']


class BookingSerializer(serializers.ModelSerializer):
    sports_ground = serializers.StringRelatedField()  # 스포츠 그라운드 이름만 반환
    facility = serializers.StringRelatedField()  # 시설 이름만 반환
    user = serializers.StringRelatedField()  # 예약한 유저의 이름만 반환
    time_slot = TimeSlotSerializer()  # 타임슬롯 정보

    class Meta:
        model = Booking
        fields = ['id', 'sports_ground', 'facility', 'user', 'time_slot', 'status']


class MatchSerializer(serializers.ModelSerializer):
    sports_ground = serializers.StringRelatedField()
    facility = serializers.StringRelatedField()

    class Meta:
        model = Match
        fields = ['id', 'sports_ground', 'facility', 'price', 'start_time', 'duration', 'status', 'match_type', 'total_spots', 'participants']


class NewsfeedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsfeedPost
        fields = ['id', 'post_type', 'post_content', 'created_at']