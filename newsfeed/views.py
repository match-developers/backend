from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import ClubPost, IndividualPost
from .serializers import ClubPostSerializer, IndividualPostSerializer


class IndividualPostsAPIView(generics.ListAPIView):
    serializer_class = IndividualPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IndividualPost.objects.filter(user=self.request.user)


class ClubPostsAPIView(generics.ListAPIView):
    serializer_class = ClubPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ClubPost.objects.filter(user=self.request.user)
