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
            
            # 리그 생성 시 LeaguePost를 생성하여 뉴스피드에 표시
            league.create_league_post()

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

        # 참가 인원이 꽉 찼을 경우 뉴스피드 포스트 업데이트
        if league.participants.count() == league.total_number_of_teams:
            league.update_league_post_for_full_participation()

        return Response({"message": "Successfully joined the league."}, status=status.HTTP_200_OK)

class LeagueMatchCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
            league_match = LeagueMatch.objects.get(match=match)
            league = league_match.league
        except (Match.DoesNotExist, LeagueMatch.DoesNotExist):
            return Response({"error": "Match or League not found."}, status=status.HTTP_404_NOT_FOUND)

        # 매치 상태를 완료로 업데이트
        if match.status == 'completed':
            return Response({"error": "This match is already completed."}, status=status.HTTP_400_BAD_REQUEST)
        
        match.status = 'completed'
        match.save()

        # 리그의 모든 매치가 완료되었는지 확인
        all_matches_completed = LeagueMatch.objects.filter(league=league, match__status__in=['scheduled', 'ongoing']).count() == 0
        
        if all_matches_completed:
            if league.current_round < league.total_number_of_rounds:
                league.current_round += 1
                league.save()

                # 다음 라운드로 전환 시 뉴스피드 포스트 업데이트
                league.update_league_post_for_new_round()

                return Response({"message": "All matches completed. Proceeding to the next round."}, status=status.HTTP_200_OK)
            else:
                # 리그가 완료된 경우 최종 포스트 업데이트
                league.update_league_post_for_completion()
                return Response({"message": "All rounds are completed. The league is finished."}, status=status.HTTP_200_OK)
        return Response({"message": "Match completed. Waiting for other matches in the round to finish."}, status=status.HTTP_200_OK)