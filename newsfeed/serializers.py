from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser

from .models import (
    Comment,
    CustomPost,
    ImageAttachment,
    TextAttachment,
    VideoAttachment,
)


class CustomPostRetrieveSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likes.count")

    class Meta:
        model = CustomPost
        fields = (
            "title",
            "user",
            "likes",
            "content_type",
            "object_id",
            "content_object",
        )
        depth = 1


class CustomPostCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, write_only=True, required=False)
    video = serializers.FileField(use_url=True, write_only=True, required=False)
    text = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomPost
        fields = (
            "user",
            "title",
            "image",
            "video",
            "text",
        )

    def validate(self, data):
        image = data.get("image")
        video = data.get("video")
        text = data.get("text")

        if (image and video) or (image and text) or (video and text):
            raise serializers.ValidationError(
                "A post can have either an image, a video, or text, but not multiple."
            )

        if not (image or video or text):
            raise serializers.ValidationError(
                "A post must have either an image, a video, or text."
            )

        return data

    def create(self, validated_data):
        image_file = validated_data.pop("image", None)
        video_file = validated_data.pop("video", None)
        text = validated_data.pop("text", None)

        custom_post = CustomPost.objects.create(**validated_data)

        if image_file is not None:
            ImageAttachment.objects.create(content_object=custom_post, image=image_file)
        elif video_file is not None:
            VideoAttachment.objects.create(content_object=custom_post, video=video_file)
        elif text is not None:
            TextAttachment.objects.create(content_object=custom_post, text=text)

        return custom_post

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"].parsers = [MultiPartParser(), FormParser()]
        return context


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
