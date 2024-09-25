from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from tournaments.models.tournament import Tournament, TournamentStatus
from tournaments.models.tournament_match import TournamentMatch
from matchmaking.models.match import Match
from matchmaking.models.team import Team
from tournaments.serializers import TournamentSerializer, TournamentStatusSerializer, TournamentMatchSerializer
from django.utils import timezone

class TournamentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TournamentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tournament = serializer.save(organizer=request.user)
            # 팀 자동 생성 및 참가
            for i in range(1, tournament.max_teams + 1):
                team = Team.objects.create(name=f"Team {i}", tournament=tournament)
                tournament.participants.add(team)
            
            tournament.save()

            # 포스트 생성
            tournament.create_tournament_post()

            return Response({
                "message": "Tournament created successfully.",
                "tournament": TournamentSerializer(tournament).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TournamentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tournament_id, *args, **kwargs):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

        tournament_serializer = TournamentSerializer(tournament)
        tournament_status = TournamentStatus.objects.filter(tournament=tournament)
        status_serializer = TournamentStatusSerializer(tournament_status, many=True)

        matches = TournamentMatch.objects.filter(tournament=tournament)
        matches_serializer = TournamentMatchSerializer(matches, many=True)

        return Response({
            "tournament": tournament_serializer.data,
            "status": status_serializer.data,
            "matches": matches_serializer.data
        }, status=status.HTTP_200_OK)


class TournamentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, tournament_id, *args, **kwargs):
        try:
            tournament = Tournament.objects.get(id=tournament_id, organizer=request.user)
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TournamentSerializer(tournament, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Tournament updated successfully.",
                "tournament": TournamentSerializer(tournament).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TournamentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, tournament_id, *args, **kwargs):
        try:
            tournament = Tournament.objects.get(id=tournament_id, organizer=request.user)
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        tournament.delete()
        return Response({"message": "Tournament deleted successfully."}, status=status.HTTP_200_OK)


class JoinTournamentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tournament_id, *args, **kwargs):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if tournament.start_date <= timezone.now().date():
            return Response({"error": "Cannot join the tournament after it has started."}, status=status.HTTP_400_BAD_REQUEST)

        if tournament.tournament_type == 'club':
            if not user.current_club:
                return Response({"error": "You must belong to a club to join this tournament."}, status=status.HTTP_400_BAD_REQUEST)
            tournament.participants.add(user.current_club)
        else:
            team = Team.objects.create(name=f"{user.username}'s Team", tournament=tournament)
            team.members.add(user)
            tournament.participants.add(team)

        tournament.save()

        # 참가 인원이 꽉 찼다면 포스트 업데이트
        tournament.update_tournament_post_on_full_participation()

        return Response({"message": "Successfully joined the tournament."}, status=status.HTTP_200_OK)


class MatchCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            match.complete()  # 경기 완료 처리
            tournament = match.tournament

            # 해당 라운드의 모든 경기가 끝났는지 확인
            remaining_matches = TournamentMatch.objects.filter(
                tournament=tournament, round_number=tournament.current_round, match__status='scheduled'
            )
            if not remaining_matches.exists():
                tournament.advance_round()  # 다음 라운드로 진행
                tournament.save()

                # 포스트 업데이트
                tournament.update_tournament_post_on_round_completion()

                return Response({"message": "Tournament advanced to the next round."}, status=status.HTTP_200_OK)
            
            return Response({"message": "Match completed successfully."}, status=status.HTTP_200_OK)

        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)