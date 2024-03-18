from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Like, MatchPost
from .serializers import MatchPostSerializer


class MatchlPostViewSet(ModelViewSet):
    queryset = MatchPost.objects.all()
    serializer_class = MatchPostSerializer
    permission_classes = [IsAuthenticated]


class LikeCommentView(APIView):
    @transaction.atomic
    def post(self, request, content_type_id, object_id, format=None):
        content_type = ContentType.objects.get_for_id(content_type_id)

        # Get the model class for the content type
        model = content_type.model_class()

        # Get the object and lock it for update
        obj = model.objects.select_for_update().get(pk=object_id)

        Like.objects.create(user=request.user, content_object=obj)
        return Response({"status": "success"})


class UnlikeCommentView(APIView):
    @transaction.atomic
    def delete(self, request, content_type_id, object_id, format=None):
        content_type = ContentType.objects.get_for_id(content_type_id)

        # Get the model class for the content type
        model = content_type.model_class()

        # Get the object and lock it for update
        obj = model.objects.select_for_update().get(pk=object_id)

        Like.objects.filter(user=request.user, content_object=obj).delete()
        return Response({"status": "success"})
