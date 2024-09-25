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
from matchmaking.views import CreateMatchView, MatchDetailView, MatchUpdateView, ManageMatchView, MatchStartView, MatchCompleteView, SearchMatchView, JoinMatchView, ManageJoinRequestView, MatchEventUpdateView, SubmitReviewView

from leagues.views import LeagueCreateView, LeagueDetailView, LeagueUpdateView, LeagueDeleteView, JoinLeagueView, LeagueMatchCompleteView

from tournaments.views import TournamentCreateView, TournamentDetailView, TournamentUpdateView, TournamentDeleteView, JoinTournamentView, MatchCompleteView
    # newsfeed/urls.py

from django.urls import path
from newsfeed.views import NewsfeedView, MatchPostDetailView, LeaguePostDetailView, TournamentPostDetailView, TransferPostDetailView, LikePostView, CommentPostView, SharePostView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # accounts 앱의 url 연결
    path('matches/create/', CreateMatchView.as_view(), name='create-match'),  # 매치 생성
    path('matches/update/<int:match_id>/', MatchUpdateView.as_view(), name='update-match'),  # 매치 수정
    path('matches/manage/<int:match_id>/', ManageMatchView.as_view(), name='manage-match'),  # 매치 관리
    path('matches/<int:match_id>/start/', MatchStartView.as_view(), name='start-match'),
    path('matches/<int:match_id>/complete/', MatchCompleteView.as_view(), name='complete-match'),
    path('matches/search/', SearchMatchView.as_view(), name='search-match'),  # 매치 검색
    path('matches/<int:match_id>/details/', MatchDetailView.as_view(), name='match-detail'),  # 매치 세부 정보 조회
    path('matches/<int:match_id>/join/', JoinMatchView.as_view(), name='join-match'),  # 매치 참가
    path('matches/<int:match_id>/join-request/<int:user_id>/', ManageJoinRequestView.as_view(), name='manage-join-request'),
    path('matches/<int:match_id>/events/', MatchEventUpdateView.as_view(), name='update-match-event'),
    path('matches/<int:match_id>/review/', SubmitReviewView.as_view(), name='submit-review'),
    
    path('create/', LeagueCreateView.as_view(), name='create_league'),
    path('<int:league_id>/', LeagueDetailView.as_view(), name='detail_league'),
    path('<int:league_id>/update/', LeagueUpdateView.as_view(), name='update_league'),
    path('<int:league_id>/delete/', LeagueDeleteView.as_view(), name='delete_league'),
    path('<int:league_id>/join/', JoinLeagueView.as_view(), name='join_league'),
    path('<int:match_id>/complete/', LeagueMatchCompleteView.as_view(), name='complete_league_match'),
    
    path('create/', TournamentCreateView.as_view(), name='create_tournament'),
    path('<int:tournament_id>/', TournamentDetailView.as_view(), name='detail_tournament'),
    path('<int:tournament_id>/update/', TournamentUpdateView.as_view(), name='update_tournament'),
    path('<int:tournament_id>/delete/', TournamentDeleteView.as_view(), name='delete_tournament'),
    path('<int:tournament_id>/join/', JoinTournamentView.as_view(), name='join_tournament'),
    path('match/<int:match_id>/complete/', MatchCompleteView.as_view(), name='complete_match'),
    
    path('newsfeed/', NewsfeedView.as_view(), name='newsfeed'),
    path('newsfeed/match/<int:post_id>/', MatchPostDetailView.as_view(), name='match_post_detail'),
    path('newsfeed/league/<int:post_id>/', LeaguePostDetailView.as_view(), name='league_post_detail'),
    path('newsfeed/tournament/<int:post_id>/', TournamentPostDetailView.as_view(), name='tournament_post_detail'),
    path('newsfeed/transfer/<int:post_id>/', TransferPostDetailView.as_view(), name='transfer_post_detail'),
    path('newsfeed/post/<int:post_id>/like/', LikePostView.as_view(), name='like_post'),
    path('newsfeed/post/<int:post_id>/comment/', CommentPostView.as_view(), name='comment_post'),
    path('newsfeed/post/<int:post_id>/share/', SharePostView.as_view(), name='share_post'),
]