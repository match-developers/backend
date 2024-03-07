from django.conf import settings
from django.shortcuts import render

import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account
from .serializers import RegistrationSerializer, UsersSerializer


class CreateAccount(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        reg_serializer = RegistrationSerializer(data=request.data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            if new_user:
                r = requests.post(
                    f"{settings.BACKEND_URL}/api-auth/token",
                    data={
                        "username": new_user.email,
                        "password": request.data["password"],
                        "client_id": settings.APPLICATION_CLIENT_ID,
                        "client_secret": settings.APPLICATION_CLIENT_SECRET,
                        "grant_type": "password",
                    },
                )
                return Response(r.json(), status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllUsers(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Account.objects.all()
    serializer_class = UsersSerializer


class CurrentUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UsersSerializer(self.request.user)
        return Response(serializer.data)
