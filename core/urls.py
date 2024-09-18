"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# core/urls.py

from django.contrib import admin
from django.urls import path, include
from matchmaking.views import MatchCreateView, MatchDetailView, MatchUpdateView, ManageMatchView, SearchMatchView, JoinMatchView, ManageJoinRequestView, MatchEventUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # accounts 앱의 url 연결
    path('matches/create/', MatchCreateView.as_view(), name='create-match'),  # 매치 생성
    path('matches/update/<int:match_id>/', MatchUpdateView.as_view(), name='update-match'),  # 매치 수정
    path('matches/manage/<int:match_id>/', ManageMatchView.as_view(), name='manage-match'),  # 매치 관리
    path('matches/search/', SearchMatchView.as_view(), name='search-match'),  # 매치 검색
    path('matches/<int:match_id>/details/', MatchDetailView.as_view(), name='match-detail'),  # 매치 세부 정보 조회
    path('matches/<int:match_id>/join/', JoinMatchView.as_view(), name='join-match'),  # 매치 참가
    path('matches/<int:match_id>/join-request/<int:user_id>/', ManageJoinRequestView.as_view(), name='manage-join-request'),
    path('matches/<int:match_id>/events/', MatchEventUpdateView.as_view(), name='update-match-event'),
]
