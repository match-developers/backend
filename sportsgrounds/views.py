from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from sportsgrounds.models.sports_ground import SportsGround, Booking
from sportsgrounds.models.facilities import Facilities, TimeSlot
from sportsgrounds.serializers import SportsGroundSerializer, BookingSerializer, TimeSlotSerializer
from matchmaking.models.match import Match
from accounts.models.users import User

# 1. 스포츠 그라운드 조회
class SportsGroundDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ground_id):
        sports_ground = get_object_or_404(SportsGround, id=ground_id)
        serializer = SportsGroundSerializer(sports_ground)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 2. 타임 슬롯 조회
class TimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, facility_id):
        facility = get_object_or_404(Facilities, id=facility_id)
        time_slots = TimeSlot.objects.filter(facility=facility)
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 3. 예약 생성
class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        facility_id = request.data.get('facility_id')
        time_slot_id = request.data.get('time_slot_id')

        facility = get_object_or_404(Facilities, id=facility_id)
        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        if time_slot.is_reserved:
            return Response({"error": "This time slot is already reserved."}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(
            sports_ground=facility.sports_ground,
            facility=facility,
            user=user,
            time_slot=time_slot,
            status="pending"
        )
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 4. 예약 승인 및 거절 (스포츠 그라운드 소유자 전용)
class ManageBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id, action):
        booking = get_object_or_404(Booking, id=booking_id)
        sports_ground = booking.sports_ground

        if not sports_ground.is_owner(request.user):
            return Response({"error": "You do not have permission to manage this booking."}, status=status.HTTP_403_FORBIDDEN)

        if action == "confirm":
            try:
                booking.confirm_booking(request.user)
                return Response({"message": "Booking confirmed."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif action == "decline":
            booking.decline_booking(request.user)
            return Response({"message": "Booking declined."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)


# 5. 예약 취소
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.user != request.user:
            return Response({"error": "You do not have permission to cancel this booking."}, status=status.HTTP_403_FORBIDDEN)

        booking.cancel_booking()
        return Response({"message": "Booking canceled successfully."}, status=status.HTTP_200_OK)


# 6. 구장 팔로우 및 언팔로우
class FollowSportsGroundView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ground_id):
        sports_ground = get_object_or_404(SportsGround, id=ground_id)
        user = request.user

        if user in sports_ground.followers.all():
            sports_ground.unfollow_ground(user)
            return Response({"message": f"Unfollowed {sports_ground.name}."}, status=status.HTTP_200_OK)
        else:
            sports_ground.follow_ground(user)
            return Response({"message": f"Followed {sports_ground.name}."}, status=status.HTTP_200_OK)