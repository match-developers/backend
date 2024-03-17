from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import ClubPost, IndividualPost
from .serializers import ClubPostSerializer, IndividualPostSerializer


class ClubPostViewSet(ModelViewSet):
    queryset = ClubPost.objects.all()
    serializer_class = ClubPostSerializer
    permission_classes = [IsAuthenticated]


class IndividualPostViewSet(ModelViewSet):
    queryset = IndividualPost.objects.all()
    serializer_class = IndividualPostSerializer
    permission_classes = [IsAuthenticated]
