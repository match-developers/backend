from django.urls import path

from .views import CustomPostViewSet, LikeCommentView, UnlikeCommentView

urlpatterns = [
    path(
        "custom_posts",
        CustomPostViewSet.as_view({"get": "list", "post": "create"}),
        name="custom_posts",
    ),
    path(
        "custom_posts/<int:pk>/",
        CustomPostViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="custom_post_detail",
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
