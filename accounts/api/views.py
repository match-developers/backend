from django.contrib.auth import logout
from django.http import JsonResponse

import requests
from allauth.account.adapter import get_adapter
from allauth.account.views import SignupView
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def get_kakao_user_info(access_token):
    # Kakao API endpoint for user information
    kakao_api_url = "https://kapi.kakao.com/v2/user/me"

    # Set the Kakao API headers
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # Make a GET request to Kakao API
    response = requests.get(kakao_api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_social_user_info(provider, access_token):
    # Define API endpoints and headers for each social provider
    social_api_endpoints = {
        "google": "https://www.googleapis.com/oauth2/v1/userinfo",
        "facebook": "https://graph.facebook.com/me",
        "apple": "https://api.apple.com/me",
        # Add more providers if needed
    }

    social_api_url = social_api_endpoints.get(provider)

    if not social_api_url:
        return None

    # Set the social API headers
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # Make a GET request to the social API
    response = requests.get(social_api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


class SocialSignupView(APIView):
    def post(self, request, *args, **kwargs):
        social_provider = request.data.get("social_provider")
        social_access_token = request.data.get("social_access_token")

        if not social_provider or not social_access_token:
            return Response(
                {"error": "Social provider and access token are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate social token and fetch user information
        social_user_info = get_social_user_info(
            social_provider, social_access_token
        )

        if not social_user_info or "id" not in social_user_info:
            return Response(
                {
                    "error": "Invalid social access token or unable to fetch user information."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Perform social signup logic
        # You need to adjust this based on your actual signup logic
        social_account = SocialAccount(
            provider=social_provider, uid=str(social_user_info["id"])
        )
        social_login = complete_social_login(request, social_account)
        get_adapter(request).save_user(request, social_login, social_login.user)

        return Response(
            {"detail": f"{social_provider} signup successful."},
            status=status.HTTP_201_CREATED,
        )


class SocialLoginView(APIView):
    def post(self, request, *args, **kwargs):
        social_provider = request.data.get("social_provider")
        social_access_token = request.data.get("social_access_token")

        if not social_provider or not social_access_token:
            return Response(
                {"error": "Social provider and access token are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate social token and fetch user information
        social_user_info = get_social_user_info(
            social_provider, social_access_token
        )

        if not social_user_info or "id" not in social_user_info:
            return Response(
                {
                    "error": "Invalid social access token or unable to fetch user information."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if a user with the social UID already exists
        try:
            social_account = SocialAccount.objects.get(
                provider=social_provider, uid=str(social_user_info["id"])
            )
        except SocialAccount.DoesNotExist:
            return Response(
                {
                    "error": f"No user associated with the provided {social_provider} account."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Perform social login logic
        social_login = complete_social_login(request, social_account)

        return Response(
            {"detail": f"{social_provider} login successful."},
            status=status.HTTP_200_OK,
        )


class KakaoSignupView(APIView):
    def post(self, request, *args, **kwargs):
        kakao_access_token = request.data.get("kakao_access_token")

        if not kakao_access_token:
            return Response(
                {"error": "Kakao access token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate Kakao token and fetch user information
        kakao_user_info = get_kakao_user_info(kakao_access_token)

        if not kakao_user_info or "id" not in kakao_user_info:
            return Response(
                {
                    "error": "Invalid Kakao access token or unable to fetch user information."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Perform social signup logic
        # You need to adjust this based on your actual signup logic
        social_account = SocialAccount(provider="kakao", uid=str(kakao_user_info["id"]))
        social_login = complete_social_login(request, social_account)
        get_adapter(request).save_user(request, social_login, social_login.user)

        return Response(
            {"detail": "Kakao signup successful."}, status=status.HTTP_201_CREATED
        )


class KakaoLoginView(APIView):
    def post(self, request, *args, **kwargs):
        kakao_access_token = request.data.get("kakao_access_token")

        if not kakao_access_token:
            return Response(
                {"error": "Kakao access token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate Kakao token and fetch user information
        kakao_user_info = get_kakao_user_info(kakao_access_token)

        if not kakao_user_info or "id" not in kakao_user_info:
            return Response(
                {
                    "error": "Invalid Kakao access token or unable to fetch user information."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if a user with the Kakao UID already exists
        try:
            social_account = SocialAccount.objects.get(
                provider="kakao", uid=str(kakao_user_info["id"])
            )
        except SocialAccount.DoesNotExist:
            return Response(
                {"error": "No user associated with the provided Kakao account."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Perform social login logic
        social_login = complete_social_login(request, social_account)

        return Response(
            {"detail": "Kakao login successful."}, status=status.HTTP_200_OK
        )


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Log out the user from all sessions
        request.auth.delete()

        # Log the user out
        logout(request)

        return JsonResponse(
            {"detail": "Logged out from all sessions successfully."},
            status=status.HTTP_200_OK,
        )


class CustomRegisterView(SignupView):
    # You can customize this view if needed
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
