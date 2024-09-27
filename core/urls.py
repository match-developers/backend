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
from django.contrib import admin
from django.urls import path, include

from matchmaking.views import CreateMatchView, MatchDetailView, MatchUpdateView, ManageMatchView, MatchStartView, MatchCompleteView, SearchMatchView, JoinMatchView, ManageJoinRequestView, MatchEventUpdateView, SubmitReviewView
from newsfeed.views import NewsfeedView, MatchPostDetailView, LeaguePostDetailView, TournamentPostDetailView, TransferPostDetailView, LikePostView, CommentPostView, SharePostView

from leagues.views import LeagueCreateView, LeagueDetailView, LeagueUpdateView, LeagueDeleteView, JoinLeagueView, LeagueMatchCompleteView
from tournaments.views import TournamentCreateView, TournamentDetailView, TournamentUpdateView, TournamentDeleteView, JoinTournamentView, MatchCompleteView

from clubs.views import ClubProfileView, FollowClubView, JoinOrQuitClubView, ManageClubMemberView, CreateLineupView, ManageTacticView
from sportsgrounds import views


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
    
        # 클럽 프로필 조회
    path('clubs/<int:club_id>/', ClubProfileView.as_view(), name='club-profile'),
    # 클럽 팔로우/언팔로우
    path('clubs/<int:club_id>/follow/', FollowClubView.as_view(), name='club-follow'),
    # 클럽 가입 요청 / 탈퇴
    path('clubs/<int:club_id>/join-or-quit/', JoinOrQuitClubView.as_view(), name='club-join-or-quit'),
    # 클럽 멤버 권한 관리 및 요청 관리
    path('clubs/<int:club_id>/manage-member/<int:member_id>/<str:action>/', ManageClubMemberView.as_view(), name='club-manage-member'),
    # 라인업 생성 및 포메이션 지정
    path('clubs/<int:club_id>/create-lineup/', CreateLineupView.as_view(), name='club-create-lineup'),
    # 택틱 관리 (생성 및 삭제)
    path('clubs/<int:club_id>/tactics/', ManageTacticView.as_view(), name='club-manage-tactic'),
    path('clubs/<int:club_id>/tactics/<int:tactic_id>/', ManageTacticView.as_view(), name='club-delete-tactic'),
    
    # 스포츠 그라운드 관련 URL
    path('sportsgrounds/', views.SportsGroundListView.as_view(), name='sportsground-list'),  # 모든 스포츠 그라운드 목록 조회
    path('sportsgrounds/<int:ground_id>/', views.SportsGroundDetailView.as_view(), name='sportsground-detail'),  # 특정 스포츠 그라운드 상세 조회
    path('sportsgrounds/<int:ground_id>/facilities/', views.FacilityListView.as_view(), name='facility-list'),  # 특정 스포츠 그라운드 내 시설 목록 조회
    path('sportsgrounds/<int:ground_id>/matches/', views.SportsGroundMatchListView.as_view(), name='sportsground-matches'),  # 특정 스포츠 그라운드에서 발생한 매치 목록 조회
    path('sportsgrounds/<int:ground_id>/follow/', views.FollowSportsGroundView.as_view(), name='sportsground-follow'),  # 스포츠 그라운드 팔로우
    path('sportsgrounds/<int:ground_id>/unfollow/', views.UnfollowSportsGroundView.as_view(), name='sportsground-unfollow'),  # 스포츠 그라운드 언팔로우

    # 시설 관련 URL
    path('facilities/<int:facility_id>/timeslots/', views.FacilityTimeSlotView.as_view(), name='facility-timeslot'),  # 특정 시설의 타임 슬롯 목록 조회

    # 예약 관련 URL
    path('bookings/', views.BookingListView.as_view(), name='booking-list'),  # 예약 목록 조회
    path('bookings/<int:booking_id>/', views.BookingDetailView.as_view(), name='booking-detail'),  # 특정 예약 상세 정보 조회
    path('bookings/<int:booking_id>/confirm/', views.ConfirmBookingView.as_view(), name='confirm-booking'),  # 예약 확정
    path('bookings/<int:booking_id>/decline/', views.DeclineBookingView.as_view(), name='decline-booking'),  # 예약 거절
    path('bookings/<int:booking_id>/cancel/', views.CancelBookingView.as_view(), name='cancel-booking'),  # 예약 취소
]