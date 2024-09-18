from rest_framework import serializers
from .models import Match

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['sports_ground', 'facility', 'price', 'start_time', 'duration', 'match_type', 'total_spots', 'league', 'tournament', 'winning_method']

    def create(self, validated_data):
        """
        매치 생성 로직을 처리하는 메소드
        """
        return Match.objects.create(**validated_data)


class MatchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['sports_ground', 'facility', 'price', 'start_time', 'duration', 'total_spots', 'status', 'match_type']

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