from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Post
from .serializers import PostSerializer


class UserPostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return Post.objects.filter(user_id=user_id)
