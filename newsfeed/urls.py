from django.urls import path

from .views import (
    ClubPostViewSet,
    IndividualPostViewSet,
    LikeCommentView,
    UnlikeCommentView,
)

urlpatterns = [
    path(
        "individual_posts/",
        IndividualPostViewSet.as_view({"get": "list", "post": "create"}),
        name="individual_posts",
    ),
    path(
        "individual_posts/<int:pk>/",
        IndividualPostViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="individual_post_detail",
    ),
    path(
        "club_posts/",
        ClubPostViewSet.as_view({"get": "list", "post": "create"}),
        name="club_posts",
    ),
    path(
        "club_posts/<int:pk>/",
        ClubPostViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="club_post_detail",
    ),
    path(
        "like/<int:content_type_id>/<int:object_id>/",
        LikeCommentView.as_view(),
        name="like_comment",
    ),
    path(
        "unlike/<int:content_type_id>/<int:object_id>/",
        UnlikeCommentView.as_view(),
        name="unlike_comment",
    ),
]
