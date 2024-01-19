from django.urls import path
from .views import SocialSignupView, SocialLoginView, KakaoSignupView, KakaoLoginView
from rest_framework.authtoken.views import obtain_auth_token
from allauth.account.views import ConfirmEmailView, PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from allauth.account.views import LoginView, LogoutView, PasswordChangeView
from accounts.api.views import CustomRegisterView, LogoutAllView

urlpatterns = [
    # Social Authentication URLs
    path('social/signup/', SocialSignupView.as_view(), name='social-signup'),
    path('social/login/', SocialLoginView.as_view(), name='social-login'),
    path('social/kakao/signup/', KakaoSignupView.as_view(), name='kakao-signup'),
    path('social/kakao/login/', KakaoLoginView.as_view(), name='kakao-login'),

    # Local Authentication URLs (Email/Password)
    path('login/', LoginView.as_view(), name='local-login'),
    path('logout/', LogoutView.as_view(), name='local-logout'),
    path('logout-all/', LogoutAllView.as_view(), name='local-logout-all'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/<slug:uidb64>/<slug:token>/', PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),
    path('register/', CustomRegisterView.as_view(), name='local-register'),
    path('confirm-email/<str:key>/', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
]
