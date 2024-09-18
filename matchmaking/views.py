from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Match
from .serializers import MatchSerializer

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