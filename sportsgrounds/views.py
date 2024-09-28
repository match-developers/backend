from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from matchmaking.serializers import MatchSerializer
from sportsgrounds.serializers import SportsGroundSerializer, BookingSerializer, TimeSlotSerializer, FacilitiesSerializer


# 1. 스포츠 그라운드 조회
class SportsGroundDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ground_id):
        sports_ground = get_object_or_404("sportsgrounds.SportsGround", id=ground_id)
        serializer = SportsGroundSerializer(sports_ground)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 2. 타임 슬롯 조회
class FacilityTimeSlotView(APIView):
    """
    특정 시설의 타임 슬롯 목록을 조회하는 뷰.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, facility_id):
        facility = get_object_or_404("sportsgrounds.Facilities", id=facility_id)
        time_slots = "sportsgrounds.TimeSlot".objects.filter(facility=facility)
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 3. 예약 생성
class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        facility_id = request.data.get('facility_id')
        time_slot_id = request.data.get('time_slot_id')

        facility = get_object_or_404("sportsgrounds.Facilities", id=facility_id)
        time_slot = get_object_or_404("sportsgrounds.TimeSlot", id=time_slot_id)

        if time_slot.is_reserved:
            return Response({"error": "This time slot is already reserved."}, status=status.HTTP_400_BAD_REQUEST)

        booking = "sportsgrounds.Booking".objects.create(
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
        booking = get_object_or_404("sportsgrounds.Booking", id=booking_id)
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
        booking = get_object_or_404("sportsgrounds.Booking", id=booking_id)

        if booking.user != request.user:
            return Response({"error": "You do not have permission to cancel this booking."}, status=status.HTTP_403_FORBIDDEN)

        booking.cancel_booking()
        return Response({"message": "Booking canceled successfully."}, status=status.HTTP_200_OK)


# 6. 구장 팔로우 및 언팔로우
class FollowSportsGroundView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ground_id):
        sports_ground = get_object_or_404("sportsgrounds.SportsGround", id=ground_id)
        user = request.user

        if user in sports_ground.followers.all():
            sports_ground.unfollow_ground(user)
            return Response({"message": f"Unfollowed {sports_ground.name}."}, status=status.HTTP_200_OK)
        else:
            sports_ground.follow_ground(user)
            return Response({"message": f"Followed {sports_ground.name}."}, status=status.HTTP_200_OK)
        
class UnfollowSportsGroundView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ground_id):
        sports_ground = get_object_or_404("sportsgrounds.SportsGround", id=ground_id)
        user = request.user

        if user in sports_ground.followers.all():
            sports_ground.unfollow_ground(user)
            return Response({"message": f"Unfollowed {sports_ground.name}."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You are not following this ground."}, status=status.HTTP_400_BAD_REQUEST)
        
class FacilityListView(APIView):
    def get(self, request, ground_id):
        try:
            sportsground = "sportsgrounds.SportsGround".objects.get(id=ground_id)
        except "sportsgrounds.SportsGround".DoesNotExist:
            return Response({"error": "Sports ground not found"}, status=status.HTTP_404_NOT_FOUND)
        
        facilities = sportsground.facilities.all()
        serializer = FacilitiesSerializer(facilities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SportsGroundMatchListView(APIView):
    def get(self, request, ground_id):
        try:
            sportsground = "sportsgrounds.SportsGround".objects.get(id=ground_id)
        except "sportsgrounds.SportsGround".DoesNotExist:
            return Response({"error": "Sports ground not found"}, status=status.HTTP_404_NOT_FOUND)
        
        matches = "matchmaking.Match".objects.filter(sports_ground=sportsground)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#booking related views
class BookingListView(APIView):
    def get(self, request):
        bookings = "sportsgrounds.Booking".objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookingDetailView(APIView):
    def get(self, request, booking_id):
        try:
            booking = "sportsgrounds.Booking".objects.get(id=booking_id)
        except "sportsgrounds.Booking".DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConfirmBookingView(APIView):
    def post(self, request, booking_id):
        try:
            booking = "sportsgrounds.Booking".objects.get(id=booking_id)
            booking.confirm_booking(request.user)
            return Response({"message": "Booking confirmed"}, status=status.HTTP_200_OK)
        except "sportsgrounds.Booking".DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

class DeclineBookingView(APIView):
    def post(self, request, booking_id):
        try:
            booking = "sportsgrounds.Booking".objects.get(id=booking_id)
            booking.decline_booking(request.user)
            return Response({"message": "Booking declined"}, status=status.HTTP_200_OK)
        except "sportsgrounds.Booking".DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

class CancelBookingView(APIView):
    def post(self, request, booking_id):
        try:
            booking = "sportsgrounds.Booking".objects.get(id=booking_id)
            booking.cancel_booking()
            return Response({"message": "Booking canceled"}, status=status.HTTP_200_OK)
        except "sportsgrounds.Booking".DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)