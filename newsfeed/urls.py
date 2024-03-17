from django.urls import path

from .views import ClubPostsAPIView, IndividualPostsAPIView

urlpatterns = [
    path(
        "individual_posts/", IndividualPostsAPIView.as_view(), name="individual_posts"
    ),
    path("club_posts/", ClubPostsAPIView.as_view(), name="individual_posts"),
]
