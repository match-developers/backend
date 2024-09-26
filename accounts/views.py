# accounts/views.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.db import models

from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status



from accounts.serializers import RegisterSerializer, LoginSerializer, SocialLoginSerializer, UserSerializer, UserStatisticsSerializer, PlaystyleTestSerializer, FollowUserSerializer
from newsfeed.serializers import NewsfeedPostSerializer

from newsfeed.models.newsfeed import NewsfeedPost
from accounts.models.users import User, UserStatistics, PlaystyleTest

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise ValidationError("Invalid email or password.")

        login(request, user)

        return Response(
            {"message": "Logged in successfully.", "user": UserSerializer(user).data}, 
            status=status.HTTP_200_OK
        )

class SocialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        return Response({"message": "Social login successful.", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
    
class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("No user with that email.")

        # Generate password reset token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build password reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Send email with the password reset link
        self.send_password_reset_email(user, reset_url)

        return Response({"message": "Password reset link sent to email."}, status=status.HTTP_200_OK)

    def send_password_reset_email(self, user, reset_url):
        """
        이메일을 보내는 로직을 별도로 함수로 분리
        """
        subject = "Reset your password"
        message = render_to_string('accounts/password_reset_email.html', {'user': user, 'reset_url': reset_url})
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        ) 
        
class UserProfileNewsfeedView(APIView):
    """
    유저가 생성/참가한 매치, 리그, 토너먼트와 관련된 뉴스피드를 조회하는 뷰
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # 유저가 생성 또는 참가한 매치, 리그, 토너먼트와 관련된 포스트만 필터링
        posts = NewsfeedPost.objects.filter(
            models.Q(creator=user) |  # 유저가 생성한 포스트
            models.Q(match__participants__user=user) |  # 유저가 참가한 매치 포스트
            models.Q(league__participants__user=user) |  # 유저가 참가한 리그 포스트
            models.Q(tournament__participants__user=user)  # 유저가 참가한 토너먼트 포스트
        ).distinct()

        serializer = NewsfeedPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class EditUserProfileView(APIView):
    """
    유저 프로필 수정을 위한 뷰
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FollowUserView(APIView):
    """
    다른 유저를 팔로우/언팔로우하는 뷰
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if target_user in user.following.all():
            user.following.remove(target_user)
            return Response({"message": f"Unfollowed {target_user.username}"}, status=status.HTTP_200_OK)
        else:
            user.following.add(target_user)
            return Response({"message": f"Followed {target_user.username}"}, status=status.HTTP_200_OK)

    def get(self, request, user_id, *args, **kwargs):
        """
        특정 유저의 팔로우/팔로워 정보 조회
        """
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FollowUserSerializer(target_user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserStatisticsView(APIView):
    """
    유저 통계 조회를 위한 뷰
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            stats = UserStatistics.objects.get(user_id=user_id)
        except UserStatistics.DoesNotExist:
            return Response({"error": "User statistics not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 간단한 20가지 질문의 예시
PLAYSTYLE_QUESTIONS = [
    "공격적인 플레이를 선호하시나요?",
    "수비적인 플레이를 선호하시나요?",
    # 나머지 18개의 질문
]

class PlaystyleTestView(APIView):
    """
    유저의 플레이스타일 테스트를 위한 뷰
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        플레이스타일 테스트 질문을 제공하는 GET 메소드
        """
        return Response({"questions": PLAYSTYLE_QUESTIONS}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        유저가 테스트를 완료한 후 결과를 저장하는 POST 메소드
        """
        user = request.user
        answers = request.data.get('answers')  # 유저가 선택한 답변
        if len(answers) != 20:
            return Response({"error": "You must answer all 20 questions."}, status=status.HTTP_400_BAD_REQUEST)

        # 결과 생성 (예: 단순히 공격형/수비형으로 분류)
        if answers.count('공격적인 플레이를 선호하시나요?') > 10:
            result = "Aggressive"
        else:
            result = "Defensive"

        # 시리얼라이저를 사용해 데이터를 저장
        playstyle_test_data = {
            'user': user.id,
            'questions': answers,
            'result': result
        }

        serializer = PlaystyleTestSerializer(data=playstyle_test_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Playstyle test completed", "result": result}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
