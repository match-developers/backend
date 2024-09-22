from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from leagues.models.league import League, LeagueStatus
from leagues.models.league_match import LeagueMatch
from matchmaking.models.match import Match
from matchmaking.models.team import Team
from leagues.serializers import LeagueSerializer, LeagueStatusSerializer, LeagueMatchSerializer
from django.utils import timezone
from rest_framework.exceptions import ValidationError

class LeagueCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LeagueSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            league = serializer.save(organizer=request.user)
            if league.league_type == 'individual':
                league.generate_teams()
            league.save()
            return Response({
                "message": "League created successfully.",
                "league": LeagueSerializer(league).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeagueDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, *args, **kwargs):
        try:
            league = League.objects.get(id=league_id)
        except League.DoesNotExist:
            return Response({"error": "League not found."}, status=status.HTTP_404_NOT_FOUND)

        league_serializer = LeagueSerializer(league)
        league_status = LeagueStatus.objects.filter(league=league)
        status_serializer = LeagueStatusSerializer(league_status, many=True)

        matches = LeagueMatch.objects.filter(league=league)
        matches_serializer = LeagueMatchSerializer(matches, many=True)

        return Response({
            "league": league_serializer.data,
            "status": status_serializer.data,
            "matches": matches_serializer.data
        }, status=status.HTTP_200_OK)


class LeagueUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, league_id, *args, **kwargs):
        try:
            league = League.objects.get(id=league_id, organizer=request.user)
        except League.DoesNotExist:
            return Response({"error": "League not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LeagueSerializer(league, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "League updated successfully.",
                "league": LeagueSerializer(league).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeagueDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, league_id, *args, **kwargs):
        try:
            league = League.objects.get(id=league_id, organizer=request.user)
        except League.DoesNotExist:
            return Response({"error": "League not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        league.delete()
        return Response({"message": "League deleted successfully."}, status=status.HTTP_200_OK)


class JoinLeagueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, league_id, *args, **kwargs):
        try:
            league = League.objects.get(id=league_id)
        except League.DoesNotExist:
            return Response({"error": "League not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if league.start_date <= timezone.now().date():
            return Response({"error": "Cannot join the league after it has started."}, status=status.HTTP_400_BAD_REQUEST)

        if league.league_type == 'club':
            if not user.current_club:
                return Response({"error": "You must belong to a club to join this league."}, status=status.HTTP_400_BAD_REQUEST)
            league.participants.add(user.current_club)
        else:
            team = Team.objects.create(name=f"{user.username}'s Team", league=league)
            team.members.add(user)
            league.participants.add(team)

        league.save()
        return Response({"message": "Successfully joined the league."}, status=status.HTTP_200_OK)


class ManageLeagueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, league_id):
        try:
            league = League.objects.get(id=league_id, organizer=request.user)
        except League.DoesNotExist:
            return Response({"error": "League not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'start':
            if league.participants.count() < league.max_teams:
                return Response({"error": "Not enough participants to start the league."}, status=status.HTTP_400_BAD_REQUEST)
            league.start_date = timezone.now().date()
            league.save()
            league.generate_schedule()  # 스케줄 생성
            return Response({"message": "League started successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)


class LeagueProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, league_id):
        try:
            league = League.objects.get(id=league_id)
        except League.DoesNotExist:
            return Response({"error": "League not found."}, status=status.HTTP_404_NOT_FOUND)

        # 라운드가 진행되었는지 체크하고, 진행 상황 업데이트
        if league.current_round < league.total_number_of_rounds:
            league.current_round += 1
            league.save()
            return Response({"message": "League round progressed to the next round."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "All rounds have been completed."}, status=status.HTTP_400_BAD_REQUEST)