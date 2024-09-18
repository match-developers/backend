from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models.match import Match, MatchEvent, TeamPlayer
from .models.team import TeamPlayer
from .serializers import MatchSerializer, MatchEventSerializer
from accounts.models.users import User

class MatchCreateView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def post(self, request, *args, **kwargs):
        serializer = MatchSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            match = serializer.save(creator=request.user)
            return Response({
                "message": "Match created successfully.",
                "match": MatchSerializer(match).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MatchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.prefetch_related('events').get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MatchSerializer(match)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MatchUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "Match not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the match is accepted by a sports ground owner
        if match.sports_ground.owner and match.status == "accepted":
            # Block updates to location or time if match is already accepted
            restricted_fields = ['sports_ground', 'start_time']
            if any(field in request.data for field in restricted_fields):
                return Response({"error": "Cannot modify location or time once the match is accepted. Please cancel the match to modify these fields."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MatchSerializer(match, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Match updated successfully.",
                "match": MatchSerializer(match).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ManageMatchView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "매치를 찾을 수 없거나 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'cancel':
            match.cancel_match()
        elif action == 'complete':
            match.complete_match()
        else:
            return Response({"error": "잘못된 액션입니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"매치 상태가 '{match.status}'로 업데이트되었습니다."}, status=status.HTTP_200_OK)
    
class SearchMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        location = request.query_params.get('location')  # Get user location
        if not location:
            return Response({"error": "Location parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use GIS to find nearby matches
        matches = Match.objects.filter(sports_ground__location__distance_lte=(location, 10000))  # 10km range
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class JoinMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        # Check for overlapping matches
        try:
            match.prevent_overlap(user)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if match.is_private:
            # Private match, send request to join
            match.join_requests.add(user)
            return Response({"message": "Request to join sent to the match owner."}, status=status.HTTP_200_OK)
        else:
            # Public match, join immediately
            team_player = TeamPlayer.objects.create(user=user, team=None)  # Assign teams later
            match.participants.add(team_player)
            return Response({"message": "Successfully joined the match."}, status=status.HTTP_200_OK)
        
class ManageJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, user_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "Match not found or you don't have permission to manage this match."}, status=status.HTTP_404_NOT_FOUND)

        try:
            requested_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Requested user not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'accept' or 'deny'
        if action == 'accept':
            if requested_user in match.join_requests.all():
                match.join_requests.remove(requested_user)
                team_player = TeamPlayer.objects.create(user=requested_user, team=None)
                match.participants.add(team_player)
                return Response({"message": f"{requested_user.username} has been added to the match."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User did not request to join this match."}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'deny':
            if requested_user in match.join_requests.all():
                match.join_requests.remove(requested_user)
                return Response({"message": f"{requested_user.username}'s join request has been denied."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User did not request to join this match."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

class MatchEventUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def post(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MatchEventSerializer(data=request.data)
        if serializer.is_valid():
            match_event = serializer.save(match=match, added_by=request.user)
            return Response({
                "message": "Match event added successfully.",
                "event": MatchEventSerializer(match_event).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)