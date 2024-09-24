from django.utils import timezone
from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models.match import Match, MatchEvent, TeamPlayer, PressConference, TeamTalk, PlayerReview, GroundReview, SportsGround
from .models.team import TeamPlayer
from .serializers import MatchSerializer, MatchEventSerializer, TeamPlayerSerializer, PlayerReviewSerializer, GroundReviewSerializer, PressConferenceSerializer
from accounts.models.users import User

class CreateMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MatchSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            match = serializer.save(creator=request.user)
            
            # 매치 생성 시 포스트 생성
            match.create_match_post()

            return Response({
                "message": "Match created successfully.",
                "match": MatchSerializer(match).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MatchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

        match_serializer = MatchSerializer(match)
        events = MatchEvent.objects.filter(match=match)
        event_serializer = MatchEventSerializer(events, many=True)

        # 선수 정보도 함께 반환
        team_players = TeamPlayer.objects.filter(team__match=match)
        player_serializer = TeamPlayerSerializer(team_players, many=True)

        return Response({
            "match": match_serializer.data,
            "events": event_serializer.data,
            "players": player_serializer.data
        }, status=status.HTTP_200_OK)
    
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
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "Match not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'cancel':
            match.cancel_match()
        elif action == 'complete':
            match.complete_match()  # 매치 완료 시 뉴스피드 업데이트
        elif action == 'start':
            match.start_match()  # 매치 시작 시 뉴스피드 업데이트
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Match status updated to '{match.status}'."}, status=status.HTTP_200_OK)

class MatchStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "Match not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        if match.status == 'scheduled':
            match.start_match()  # 매치 시작 로직
            return Response({"message": "Match started successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Cannot start a match that is not scheduled."}, status=status.HTTP_400_BAD_REQUEST)
        
class MatchCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, creator=request.user)
        except Match.DoesNotExist:
            return Response({"error": "Match not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        if match.status == 'ongoing':
            match.complete_match()  # 매치 완료 로직
            return Response({"message": "Match completed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Cannot complete a match that is not ongoing."}, status=status.HTTP_400_BAD_REQUEST)
    
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
    
class PlayerUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def post(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # 교체할 선수와 교체된 선수 정보 가져오기
        in_player_id = request.data.get('in_player_id')  # 교체된 선수 ID
        out_player_id = request.data.get('out_player_id')  # 교체된 선수 ID

        try:
            in_player = TeamPlayer.objects.get(id=in_player_id)
            out_player = TeamPlayer.objects.get(id=out_player_id)
        except TeamPlayer.DoesNotExist:
            return Response({"error": "Player not found."}, status=status.HTTP_404_NOT_FOUND)

        # 교체 처리: 선발 여부 수정
        out_player.is_starting_player = False
        in_player.is_starting_player = True
        out_player.save()
        in_player.save()

        # 매치 이벤트 생성
        MatchEvent.objects.create(
            match=match,
            event_type='substitution',
            timestamp=timezone.now(),
            added_by=request.user,
            target_player=out_player
        )

        return Response({"message": "Player substitution successful."}, status=status.HTTP_200_OK)


class PressConferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id, *args, **kwargs):
        """
        Press Conference 정보를 불러오는 뷰
        """
        try:
            press_conference = PressConference.objects.get(match_id=match_id)
        except PressConference.DoesNotExist:
            return Response({"error": "Press Conference not found."}, status=status.HTTP_404_NOT_FOUND)

        # Press Conference 정보 반환 (참가자, 질문 등)
        serializer = PressConferenceSerializer(press_conference)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, match_id, *args, **kwargs):
        """
        질문 생성 및 답변 처리. 처음 호출 시 질문을 생성하고, 그 후로는 답변을 받아 처리.
        """
        try:
            press_conference = PressConference.objects.get(match_id=match_id)
        except PressConference.DoesNotExist:
            return Response({"error": "Press Conference not found."}, status=status.HTTP_404_NOT_FOUND)

        # 질문 생성이 필요하면
        if not press_conference.questions:
            press_conference.generate_questions()
            return Response({"message": "Questions generated successfully."}, status=status.HTTP_201_CREATED)

        # 질문이 이미 생성된 경우, 답변을 처리하고 다음 질문을 반환
        answer = request.data.get("answer", "")
        if answer:
            next_question = press_conference.process_answer(answer)
            return Response({"next_question": next_question}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Answer not provided."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, match_id, *args, **kwargs):
        """
        대화를 추가로 이어갈 때 사용할 수 있는 뷰.
        """
        try:
            press_conference = PressConference.objects.get(match_id=match_id)
        except PressConference.DoesNotExist:
            return Response({"error": "Press Conference not found."}, status=status.HTTP_404_NOT_FOUND)

        # 추가 대화 저장
        chat_message = request.data.get("message", "")
        if chat_message:
            press_conference.process_answer(chat_message)
            return Response({"message": "Chat message saved."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Message not provided."}, status=status.HTTP_400_BAD_REQUEST)

class StartPressConferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, *args, **kwargs):
        """
        Press Conference 시작 뷰. 처음 실행 시 사용자를 참가자로 추가하고, 첫 질문 생성.
        """
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

        # 이미 Press Conference가 있으면
        if PressConference.objects.filter(match=match).exists():
            return Response({"error": "Press Conference already exists for this match."}, status=status.HTTP_400_BAD_REQUEST)

        # Press Conference 생성
        press_conference = PressConference.objects.create(match=match)
        press_conference.participants.set(match.participants.all())  # 참가자 설정
        press_conference.generate_questions()  # 질문 생성

        return Response({"message": "Press Conference started and questions generated."}, status=status.HTTP_201_CREATED)
    
class TeamTalkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, team_id):
        try:
            match = Match.objects.get(id=match_id)
            team = TeamPlayer.objects.get(id=team_id, match=match)
        except (Match.DoesNotExist, TeamPlayer.DoesNotExist):
            return Response({"error": "Match or team not found."}, status=status.HTTP_404_NOT_FOUND)

        # 채팅 메시지 가져오기
        message = request.data.get('message')
        if not message:
            return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 채팅 로그에 저장
        team_talk, created = TeamTalk.objects.get_or_create(match=match, team=team)
        team_talk.chat_log.append({
            "user": request.user.username,
            "message": message,
            "timestamp": timezone.now().isoformat(),
        })
        team_talk.save()

        return Response({"message": "Message sent.", "chat_log": team_talk.chat_log}, status=status.HTTP_200_OK)
    
class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

        # 플레이어 리뷰 작성
        players = match.participants.exclude(user=request.user)
        for player in players:
            review_data = request.data.get(f'player_{player.id}', None)
            if review_data:
                player_review_serializer = PlayerReviewSerializer(data=review_data)
                if player_review_serializer.is_valid():
                    PlayerReview.objects.create(
                        match=match,
                        reviewer=request.user,
                        player=player.user,
                        **player_review_serializer.validated_data
                    )
                else:
                    return Response(player_review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 구장 리뷰 작성
        ground_review_data = request.data.get('ground_review', None)
        if ground_review_data:
            ground_review_serializer = GroundReviewSerializer(data=ground_review_data)
            if ground_review_serializer.is_valid():
                GroundReview.objects.create(
                    match=match,
                    reviewer=request.user,
                    ground=match.sports_ground,
                    **ground_review_serializer.validated_data
                )
            else:
                return Response(ground_review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Reviews submitted successfully."}, status=status.HTTP_201_CREATED)