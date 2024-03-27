from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Comment, CustomPost, ImageAttachment, VideoAttachment


class ImageAttachmentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ImageAttachment
        fields = ("image",)
        extra_kwargs = {
            "content_object": {"required": False},
        }


class VideoAttachmentSerializer(serializers.ModelSerializer):
    video = serializers.FileField(use_url=True)

    class Meta:
        model = VideoAttachment
        fields = ("video",)
        extra_kwargs = {
            "content_object": {"required": False},
        }


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

    class Meta:
        model = CustomPost
        fields = (
            "user",
            "title",
            "image",
            "video",
        )

    def validate(self, data):
        if "image" in data and "video" in data:
            raise serializers.ValidationError(
                "A post can have either an image or a video, but not both."
            )
        return data

    def create(self, validated_data):
        image_file = validated_data.pop("image", None)
        video_file = validated_data.pop("video", None)

        custom_post = CustomPost.objects.create(**validated_data)

        if image_file is not None:
            ImageAttachment.objects.create(content_object=custom_post, image=image_file)
        elif video_file is not None:
            VideoAttachment.objects.create(content_object=custom_post, video=video_file)

        return custom_post

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"].parsers = [MultiPartParser(), FormParser()]
        return context


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
