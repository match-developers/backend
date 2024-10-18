from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.db import models
from django.apps import apps

from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    SocialLoginSerializer,
    UserSerializer,
    UserStatisticsSerializer,
    PlaystyleTestSerializer,
    FollowUserSerializer,
    PasswordChangeSerializer,
)
from newsfeed.serializers import NewsfeedPostSerializer

# User 모델 문자열 참조

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = models.get_model('accounts', 'User').objects.get(id=user_id)  # 문자열 참조로 User 접근
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.get_model('accounts', 'User').DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(status=204)

class RegisterView(generics.CreateAPIView):
    queryset = "accounts.User"  # User 모델 문자열 참조
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

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        
        user = "accounts.User".objects.filter(email=email).first()  # User 모델 문자열 참조
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
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = "accounts.User".objects.get(id=user_id)  # User 모델 문자열 참조
        except "accounts.User".DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        posts = "newsfeed.NewsfeedPost".objects.filter(  # NewsfeedPost 모델 문자열 참조
            models.Q(creator=user) |
            models.Q(match__participants__user=user) |
            models.Q(league__participants__user=user) |
            models.Q(tournament__participants__user=user)
        ).distinct()

        serializer = NewsfeedPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EditUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        try:
            target_user = "accounts.User".objects.get(id=user_id)  # User 모델 문자열 참조
        except "accounts.User".DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if target_user in user.following.all():
            user.following.remove(target_user)
            return Response({"message": f"Unfollowed {target_user.username}"}, status=status.HTTP_200_OK)
        else:
            user.following.add(target_user)
            return Response({"message": f"Followed {target_user.username}"}, status=status.HTTP_200_OK)

    def get(self, request, user_id, *args, **kwargs):
        try:
            target_user = "accounts.User".objects.get(id=user_id)  # User 모델 문자열 참조
        except "accounts.User".DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FollowUserSerializer(target_user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            stats = "accounts.UserStatistics".objects.get(user_id=user_id)  # UserStatistics 모델 문자열 참조
        except "accounts.UserStatistics".DoesNotExist:
            return Response({"error": "User statistics not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

        
class UpdatePlaystyleView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        playstyle_result = request.data.get('result')
        questions = request.data.get('questions')

        if not playstyle_result or not questions:
            return Response(
                {"error": "Both playstyle result and questions are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # UserStatistics와 PlaystyleTest 모델을 동적으로 가져오기
        UserStatistics = apps.get_model('accounts', 'UserStatistics')
        PlaystyleTest = apps.get_model('your_app_name', 'PlaystyleTest')  # 'your_app_name'은 해당 모델의 앱 이름으로 교체

        try:
            user_statistics = UserStatistics.objects.get(user=request.user)

            # PlaystyleTest 업데이트 또는 생성
            playstyle_test, created = PlaystyleTest.objects.update_or_create(
                user_statistics=user_statistics,
                defaults={
                    'questions': questions,
                    'result': playstyle_result
                }
            )

            serializer = PlaystyleTestSerializer(playstyle_test)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserStatistics.DoesNotExist:
            return Response(
                {"error": "User statistics not found."},
                status=status.HTTP_404_NOT_FOUND
            )