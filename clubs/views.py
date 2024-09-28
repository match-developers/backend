from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

### 1. 클럽 프로필 조회
class ClubProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
        except "clubs.Club".DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        # 클럽 기본 정보와 통계 정보 반환
        club_serializer = "clubs.serializers.ClubSerializer"(club)  # 문자열 참조
        club_stats = "clubs.ClubStatistics".objects.get(club=club)  # 문자열 참조
        stats_serializer = "clubs.serializers.ClubStatisticsSerializer"(club_stats)  # 문자열 참조
        
        # 클럽 관련 뉴스피드 게시물
        newsfeed_posts = "newsfeed.NewsfeedPost".objects.filter(club=club)  # 문자열 참조
        newsfeed_serializer = "newsfeed.serializers.NewsfeedPostSerializer"(newsfeed_posts, many=True)  # 문자열 참조
        
        # 클럽 멤버 목록
        members = club.members.all()
        member_serializer = "clubs.serializers.ClubMemberSerializer"(members, many=True)  # 문자열 참조

        return Response({
            "club": club_serializer.data,
            "statistics": stats_serializer.data,
            "newsfeed": newsfeed_serializer.data,
            "members": member_serializer.data,
        }, status=status.HTTP_200_OK)

### 2. 클럽 팔로우/언팔로우
class FollowClubView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
        except "clubs.Club".DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        followers = club.followers if club.followers else []

        if user.id in followers:
            followers.remove(user.id)
            club.followers = followers
            club.save()
            return Response({"message": f"Unfollowed {club.name}"}, status=status.HTTP_200_OK)
        else:
            followers.append(user.id)
            club.followers = followers
            club.save()
            return Response({"message": f"Followed {club.name}"}, status=status.HTTP_200_OK)

### 3. 클럽 가입 요청 / 탈퇴
class JoinOrQuitClubView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
        except "clubs.Club".DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user in club.members.all():
            # 클럽 탈퇴 로직
            club.remove_member(user)
            return Response({"message": "Successfully quit the club."}, status=status.HTTP_200_OK)
        else:
            # 클럽 가입 요청 로직
            club.add_member(user)
            return Response({"message": "Successfully joined the club."}, status=status.HTTP_200_OK)

### 4. 멤버 관리 및 권한 설정
class ManageClubMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id, member_id, action):
        """
        action은 'assign_permission', 'remove_permission', 'accept_request', 'decline_request' 중 하나.
        """
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
            member = "accounts.User".objects.get(id=member_id)  # 문자열 참조
        except ("clubs.Club".DoesNotExist, "accounts.User".DoesNotExist):
            return Response({"error": "Club or member not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        # 권한 확인: 소유자거나 해당 권한이 있어야 한다
        if not club.is_owner(user) and not club.has_permission(user, 'manage_requests'):
            return Response({"error": "You do not have permission to manage members or requests."}, status=status.HTTP_403_FORBIDDEN)

        if action == 'assign_permission':
            permission_type = request.data.get('permission_type')
            if not club.has_permission(user, 'assign_owner'):
                return Response({"error": "You do not have permission to assign permissions."}, status=status.HTTP_403_FORBIDDEN)
            club.assign_permission(member, permission_type)
            return Response({"message": f"Assigned {permission_type} to {member.username}."}, status=status.HTTP_200_OK)

        elif action == 'remove_permission':
            permission_type = request.data.get('permission_type')
            if not club.has_permission(user, 'assign_owner'):
                return Response({"error": "You do not have permission to remove permissions."}, status=status.HTTP_403_FORBIDDEN)
            club.remove_permission(member, permission_type)
            return Response({"message": f"Removed {permission_type} from {member.username}."}, status=status.HTTP_200_OK)

        elif action == 'accept_request':
            if club.has_permission(user, 'manage_requests'):
                club.accept_join_request(member)
                return Response({"message": f"Accepted {member.username}'s join request."}, status=status.HTTP_200_OK)

        elif action == 'decline_request':
            if club.has_permission(user, 'manage_requests'):
                club.decline_join_request(member)
                return Response({"message": f"Declined {member.username}'s join request."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

### 5. 라인업 생성 및 포메이션 지정
class CreateLineupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
        except "clubs.Club".DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not club.is_owner(user) and not club.has_permission(user, 'manage_team'):
            return Response({"error": "You do not have permission to create a lineup."}, status=status.HTTP_403_FORBIDDEN)

        # 선발, 교체 멤버 및 포메이션 정보 저장
        starters = request.data.get('starters')  # 선발 멤버
        substitutes = request.data.get('substitutes')  # 교체 멤버
        formation = request.data.get('formation')  # 포메이션 정보 (아이콘 위치)

        # 라인업 생성 로직 (추가 상세 로직은 Club 모델에서 구현)
        club.create_lineup(starters, substitutes, formation)
        return Response({"message": "Lineup and formation created successfully."}, status=status.HTTP_201_CREATED)

### 6. 택틱 관리
class ManageTacticView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id):
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
        except "clubs.Club".DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not club.is_owner(user) and not club.has_permission(user, 'manage_team'):
            return Response({"error": "You do not have permission to manage tactics."}, status=status.HTTP_403_FORBIDDEN)

        tactic_name = request.data.get('tactic_name')
        tactic_explanation = request.data.get('tactic_explanation')

        # 택틱 생성 로직
        tactic = club.create_tactic(request.user, tactic_name, tactic_explanation)
        return Response({"message": "Tactic created successfully.", "tactic": tactic_explanation}, status=status.HTTP_201_CREATED)

    def delete(self, request, club_id, tactic_id):
        """
        특정 전술을 삭제하는 로직
        """
        try:
            club = "clubs.Club".objects.get(id=club_id)  # 문자열 참조
            tactic = club.tactics.get(id=tactic_id)  # 문자열 참조
        except ("clubs.Club".DoesNotExist, "clubs.Tactic".DoesNotExist):
            return Response({"error": "Club or tactic not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not club.is_owner(user) and not club.has_permission(user, 'manage_team'):
            return Response({"error": "You do not have permission to delete tactics."}, status=status.HTTP_403_FORBIDDEN)

        tactic.delete()
        return Response({"message": "Tactic deleted successfully."}, status=status.HTTP_200_OK)