from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import models
from django.contrib.gis.db.models.functions import Distance  # GeoDjango distance function for location-based queries

from newsfeed.serializers import NewsfeedPostSerializer, MatchPostSerializer, LeaguePostSerializer, TournamentPostSerializer, TransferPostSerializer


class NewsfeedView(APIView):
    """
    유저의 뉴스피드를 조회하는 뷰
    """
    def get(self, request):
        user = request.user
        try:
            # 유저의 뉴스피드 가져오기
            newsfeed = "newsfeed.Newsfeed".objects.get(user=user)
        except "newsfeed.Newsfeed".DoesNotExist:
            return Response({"error": "No newsfeed found for this user"}, status=status.HTTP_404_NOT_FOUND)

        # 팔로우한 유저, 클럽, 그리고 스포츠 그라운드 가져오기
        followed_users = user.following.all()
        followed_clubs = user.followed_clubs.all()  # 팔로우한 클럽이 있다고 가정
        followed_grounds = user.followed_grounds.all()  # 팔로우한 스포츠 그라운드 목록

        # 위치 기반 필터링을 위한 위치 정보
        user_location = user.location  # 유저의 위치 정보

        # 관련된 뉴스피드 포스트 필터링
        posts = "newsfeed.NewsfeedPost".objects.filter(
            models.Q(creator=user) |  # 유저가 생성한 포스트
            models.Q(creator__in=followed_users) |  # 유저가 팔로우한 사람이 생성한 포스트
            models.Q(match__participants__user=user) |  # 유저가 참가한 매치 포스트
            models.Q(match__participants__user__in=followed_users) |  # 팔로우한 사람이 참가한 매치 포스트
            models.Q(league__participants__user=user) |  # 유저가 참가한 리그 포스트
            models.Q(league__participants__user__in=followed_users) |  # 팔로우한 사람이 참가한 리그 포스트
            models.Q(tournament__participants__user=user) |  # 유저가 참가한 토너먼트 포스트
            models.Q(tournament__participants__user__in=followed_users) |  # 팔로우한 사람이 참가한 토너먼트 포스트
            models.Q(match__participants__club__in=followed_clubs) |  # 팔로우한 클럽의 매치 포스트
            models.Q(league__participants__club__in=followed_clubs) |  # 팔로우한 클럽의 리그 포스트
            models.Q(tournament__participants__club__in=followed_clubs) |  # 팔로우한 클럽의 토너먼트 포스트
            models.Q(match__sports_ground__in=followed_grounds)  # 팔로우한 스포츠 그라운드에서 일어나는 매치 포스트
        ).distinct()

        # 가까운 지역의 매치, 리그, 토너먼트 포스트 필터링
        nearby_matches = "matchmaking.Match".objects.annotate(
            distance=Distance('location', user_location)
        ).filter(distance__lte=5000)  # 5km 이내의 매치
        nearby_leagues = "leagues.League".objects.annotate(
            distance=Distance('location', user_location)
        ).filter(distance__lte=5000)  # 5km 이내의 리그
        nearby_tournaments = "tournaments.Tournament".objects.annotate(
            distance=Distance('location', user_location)
        ).filter(distance__lte=5000)  # 5km 이내의 토너먼트

        # 위치 기반의 포스트도 필터링된 posts에 포함
        nearby_posts = "newsfeed.NewsfeedPost".objects.filter(
            models.Q(match__in=nearby_matches) |
            models.Q(league__in=nearby_leagues) |
            models.Q(tournament__in=nearby_tournaments)
        ).distinct()

        # 최종 포스트 리스트: 필터링된 포스트 + 위치 기반 포스트
        all_posts = posts.union(nearby_posts)

        # 직렬화하여 응답 반환
        serializer = NewsfeedPostSerializer(all_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikePostView(APIView):
    """
    뉴스피드 포스트에 좋아요를 추가하는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        post.add_like()
        return Response({"message": "Like added successfully", "likes": post.likes}, status=status.HTTP_200_OK)


class CommentPostView(APIView):
    """
    뉴스피드 포스트에 댓글을 추가하는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        comment = request.data.get('comment')
        if not comment:
            return Response({"error": "Comment content is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        post.add_comment(comment)
        return Response({"message": "Comment added successfully", "comments": post.comments}, status=status.HTTP_200_OK)


class SharePostView(APIView):
    """
    뉴스피드 포스트를 공유하는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        post.add_share()
        return Response({"message": "Post shared successfully", "shares": post.shares}, status=status.HTTP_200_OK)


class ViewPostDetailView(APIView):
    """
    특정 포스트의 전체 화면 조회 (매치, 리그, 토너먼트, 트랜스퍼) 뷰
    """
    def get(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        if post.post_type == 'match':
            match_post = get_object_or_404("newsfeed.MatchPost", newsfeed_post=post)
            serializer = MatchPostSerializer(match_post)
        elif post.post_type == 'league':
            league_post = get_object_or_404("newsfeed.LeaguePost", newsfeed_post=post)
            serializer = LeaguePostSerializer(league_post)
        elif post.post_type == 'tournament':
            tournament_post = get_object_or_404("newsfeed.TournamentPost", newsfeed_post=post)
            serializer = TournamentPostSerializer(tournament_post)
        elif post.post_type == 'transfer':
            transfer_post = get_object_or_404("newsfeed.TransferPost", newsfeed_post=post)
            serializer = TransferPostSerializer(transfer_post)
        else:
            return Response({"error": "Invalid post type"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EditPostView(APIView):
    """
    뉴스피드 포스트를 수정하는 뷰 (권한이 있는 경우)
    """
    def put(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        if post.newsfeed.user != request.user:
            return Response({"error": "You do not have permission to edit this post"}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get('content')
        if not new_content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        post.edit_post(new_content)
        return Response({"message": "Post edited successfully"}, status=status.HTTP_200_OK)


class DeletePostView(APIView):
    """
    뉴스피드 포스트를 삭제하는 뷰 (권한이 있는 경우)
    """
    def delete(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        if post.newsfeed.user != request.user:
            return Response({"error": "You do not have permission to delete this post"}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)


class HidePostView(APIView):
    """
    뉴스피드 포스트를 숨기는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404("newsfeed.NewsfeedPost", id=post_id)
        # 포스트를 숨기는 로직을 여기에 구현
        post.hidden = True
        post.save()
        return Response({"message": "Post hidden successfully"}, status=status.HTTP_200_OK)
    
# Match Post 상세 정보 조회
class MatchPostDetailView(APIView):
    def get(self, request, post_id):
        try:
            match_post = "newsfeed.MatchPost".objects.get(id=post_id)
        except "newsfeed.MatchPost".DoesNotExist:
            return Response({"error": "Match post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MatchPostSerializer(match_post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# League Post 상세 정보 조회
class LeaguePostDetailView(APIView):
    def get(self, request, post_id):
        try:
            league_post = "newsfeed.LeaguePost".objects.get(id=post_id)
        except "newsfeed.LeaguePost".DoesNotExist:
            return Response({"error": "League post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LeaguePostSerializer(league_post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Tournament Post 상세 정보 조회
class TournamentPostDetailView(APIView):
    def get(self, request, post_id):
        try:
            tournament_post = "newsfeed.TournamentPost".objects.get(id=post_id)
        except "newsfeed.TournamentPost".DoesNotExist:
            return Response({"error": "Tournament post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TournamentPostSerializer(tournament_post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Transfer Post 상세 정보 조회
class TransferPostDetailView(APIView):
    def get(self, request, post_id):
        try:
            transfer_post = "newsfeed.TransferPost".objects.get(id=post_id)
        except "newsfeed.TransferPost".DoesNotExist:
            return Response({"error": "Transfer post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TransferPostSerializer(transfer_post)
        return Response(serializer.data, status=status.HTTP_200_OK)