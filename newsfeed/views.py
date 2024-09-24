from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from newsfeed.models.newsfeed import Newsfeed, NewsfeedPost
from newsfeed.models.match_post import MatchPost
from newsfeed.models.league_post import LeaguePost
from newsfeed.models.tournament_post import TournamentPost
from newsfeed.models.transfer_post import TransferPost
from newsfeed.serializers import NewsfeedPostSerializer, MatchPostSerializer, LeaguePostSerializer, TournamentPostSerializer, TransferPostSerializer


class NewsfeedView(APIView):
    """
    유저의 뉴스피드를 조회하는 뷰
    """
    def get(self, request):
        user = request.user
        try:
            newsfeed = Newsfeed.objects.get(user=user)
        except Newsfeed.DoesNotExist:
            return Response({"error": "No newsfeed found for this user"}, status=status.HTTP_404_NOT_FOUND)

        posts = newsfeed.posts.all()
        serializer = NewsfeedPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikePostView(APIView):
    """
    뉴스피드 포스트에 좋아요를 추가하는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404(NewsfeedPost, id=post_id)
        post.add_like()
        return Response({"message": "Like added successfully", "likes": post.likes}, status=status.HTTP_200_OK)


class CommentPostView(APIView):
    """
    뉴스피드 포스트에 댓글을 추가하는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404(NewsfeedPost, id=post_id)
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
        post = get_object_or_404(NewsfeedPost, id=post_id)
        post.add_share()
        return Response({"message": "Post shared successfully", "shares": post.shares}, status=status.HTTP_200_OK)


class ViewPostDetailView(APIView):
    """
    특정 포스트의 전체 화면 조회 (매치, 리그, 토너먼트, 트랜스퍼) 뷰
    """
    def get(self, request, post_id):
        post = get_object_or_404(NewsfeedPost, id=post_id)
        if post.post_type == 'match':
            match_post = get_object_or_404(MatchPost, newsfeed_post=post)
            serializer = MatchPostSerializer(match_post)
        elif post.post_type == 'league':
            league_post = get_object_or_404(LeaguePost, newsfeed_post=post)
            serializer = LeaguePostSerializer(league_post)
        elif post.post_type == 'tournament':
            tournament_post = get_object_or_404(TournamentPost, newsfeed_post=post)
            serializer = TournamentPostSerializer(tournament_post)
        elif post.post_type == 'transfer':
            transfer_post = get_object_or_404(TransferPost, newsfeed_post=post)
            serializer = TransferPostSerializer(transfer_post)
        else:
            return Response({"error": "Invalid post type"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EditPostView(APIView):
    """
    뉴스피드 포스트를 수정하는 뷰 (권한이 있는 경우)
    """
    def put(self, request, post_id):
        post = get_object_or_404(NewsfeedPost, id=post_id)
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
        post = get_object_or_404(NewsfeedPost, id=post_id)
        if post.newsfeed.user != request.user:
            return Response({"error": "You do not have permission to delete this post"}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)


class HidePostView(APIView):
    """
    뉴스피드 포스트를 숨기는 뷰
    """
    def post(self, request, post_id):
        post = get_object_or_404(NewsfeedPost, id=post_id)
        # 포스트를 숨기는 로직을 여기에 구현
        post.hidden = True
        post.save()
        return Response({"message": "Post hidden successfully"}, status=status.HTTP_200_OK)
    
# Match Post 상세 정보 조회
class MatchPostDetailView(APIView):
    def get(self, request, post_id):
        try:
            match_post = MatchPost.objects.get(id=post_id)
        except MatchPost.DoesNotExist:
            return Response({"error": "Match post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MatchPostSerializer(match_post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# League Post 상세 정보 조회
class LeaguePostDetailView(APIView):
    def get(self, request, post_id):
        try:
            league_post = LeaguePost.objects.get(id=post_id)
        except LeaguePost.DoesNotExist:
            return Response({"error": "League post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LeaguePostSerializer(league_post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Tournament Post 상세 정보 조회
class TournamentPostDetailView(APIView):
    def get(self, request, post_id):
        try:
            tournament_post = TournamentPost.objects.get(id=post_id)
        except TournamentPost.DoesNotExist:
            return Response({"error": "Tournament post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TournamentPostSerializer(tournament_post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Transfer Post 상세 정보 조회
class TransferPostDetailView(APIView):
    def get(self, request, post_id):
        try:
            transfer_post = TransferPost.objects.get(id=post_id)
        except TransferPost.DoesNotExist:
            return Response({"error": "Transfer post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TransferPostSerializer(transfer_post)
        return Response(serializer.data, status=status.HTTP_200_OK)