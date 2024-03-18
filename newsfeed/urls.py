from django.urls import path

from .views import LikeCommentView, MatchlPostViewSet, UnlikeCommentView

urlpatterns = [
    path(
        "match_posts/",
        MatchlPostViewSet.as_view({"get": "list", "post": "create"}),
        name="match_posts",
    ),
    path(
        "match_posts/<int:pk>/",
        MatchlPostViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="match_post_detail",
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
