# accounts/urls.py

from django.urls import path
from .views import UserProfileView, RegisterView, LoginView, SocialLoginView, PasswordResetView, UserProfileNewsfeedView, EditUserProfileView, FollowUserView, UserStatisticsView, PlaystyleTestView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('social-login/', SocialLoginView.as_view(), name='social_login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
        # 유저 프로필 뉴스피드 조회
    path('user/<int:user_id>/newsfeed/', UserProfileNewsfeedView.as_view(), name='user-profile-newsfeed'),
    
    # 유저 프로필 수정
    path('user/profile/edit/', EditUserProfileView.as_view(), name='edit-user-profile'),
    
    # 팔로우/언팔로우
    path('user/<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    
    # 유저 통계 조회
    path('user/<int:user_id>/statistics/', UserStatisticsView.as_view(), name='user-statistics'),
    
    # 플레이스타일 테스트
    path('user/playstyle-test/', PlaystyleTestView.as_view(), name='playstyle-test'),
    
    path('user/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),

]