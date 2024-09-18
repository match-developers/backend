from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models.match import Match
from .models.team import TeamPlayer
from .serializers import MatchSerializer
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
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def get(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
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
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def get(self, request, *args, **kwargs):
        # 검색 조건을 쿼리 파라미터로 받아오기
        match_type = request.query_params.get('match_type')
        date = request.query_params.get('date')
        location = request.query_params.get('location')

        # 조건에 따라 매치 필터링
        matches = Match.objects.all()
        
        if match_type:
            matches = matches.filter(match_type=match_type)
        if date:
            matches = matches.filter(start_time__date=date)
        if location:
            matches = matches.filter(sports_ground__name__icontains=location)  # 구장 이름으로 검색

        # 검색된 매치 리스트를 반환
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class JoinMatchView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def post(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        if match.is_private:
            # 비공개 매치인 경우, 참가 요청을 생성
            match.join_requests.add(user)
            return Response({"message": "Request to join sent to the match owner."}, status=status.HTTP_200_OK)
        else:
            # 공개 매치인 경우, 바로 참가
            team_player = TeamPlayer.objects.create(user=user, team=None)  # 팀 할당은 추후
            match.participants.add(team_player)
            return Response({"message": "Successfully joined the match."}, status=status.HTTP_200_OK)
        
class ManageJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, user_id, *args, **kwargs):
        """
        매치 생성자가 참가 요청을 승인하거나 거부하는 로직
        """
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "Match not found or you don't have permission to manage this match."}, status=status.HTTP_404_NOT_FOUND)

        try:
            requested_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Requested user not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'accept' 또는 'deny'를 받아 처리
        if action == 'accept':
            # 참가 요청 승인
            if requested_user in match.join_requests.all():
                match.join_requests.remove(requested_user)
                team_player = TeamPlayer.objects.create(user=requested_user, team=None)  # 팀 할당은 추후에 가능
                match.participants.add(team_player)
                return Response({"message": f"{requested_user.username} has been added to the match."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User did not request to join this match."}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'deny':
            # 참가 요청 거부
            if requested_user in match.join_requests.all():
                match.join_requests.remove(requested_user)
                return Response({"message": f"{requested_user.username}'s join request has been denied."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User did not request to join this match."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)