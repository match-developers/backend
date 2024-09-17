# accounts/views.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import login

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer, SocialLoginSerializer, UserSerializer
from .models import User

from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate

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