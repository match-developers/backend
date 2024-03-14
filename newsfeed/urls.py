from django.urls import path

from .views import UserPostsAPIView

urlpatterns = [
    path("posts/", UserPostsAPIView.as_view(), name="user_posts"),
]
