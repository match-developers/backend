import imghdr
import os

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser

from matchmaking.models import MatchPost
from matchmaking.serializers import MatchPostSerializer

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
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(), slug_field="model", required=False
    )
    object_id = serializers.IntegerField(required=False)
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = CustomPost
        fields = (
            "id",
            "user",
            "title",
            "image",
            "video",
            "text",
            "content_type",
            "object_id",
            "content_object",
        )

    def validate(self, data):
        image = data.get("image")
        video = data.get("video")
        text = data.get("text")
        content_type = data.get("content_type")

        if not content_type:
            if (image and video) or (image and text) or (video and text):
                raise serializers.ValidationError(
                    "A post can have either an image, a video, or text, but not multiple."
                )

            if not (image or video or text):
                raise serializers.ValidationError(
                    "A post must have either an image, a video, or text."
                )
        return data

    def validate_image(self, value):
        image_type = imghdr.what(None, h=value.read()).lower()
        if image_type not in ["jpeg", "png", "gif"]:
            raise serializers.ValidationError(
                "Invalid image format. Only JPG, JPEG, PNG, and GIF are allowed."
            )

        # Important: rewind the image file to the beginning after reading
        value.seek(0)

        image_type_by_name = os.path.splitext(value.name)[1].lower()
        if image_type_by_name not in [".jpg", ".jpeg", ".png", ".gif"]:
            raise serializers.ValidationError(
                "Invalid image format. Only JPG, JPEG, PNG, and GIF are allowed."
            )

        if (
            not (image_type == "jpeg" and image_type_by_name in [".jpg", ".jpeg"])
            and image_type_by_name != f".{image_type}"
        ):
            raise serializers.ValidationError(
                "File extension does not match image format."
            )
        return value

    def validate_video(self, value):
        # Get the extension of the file
        video_type_by_name = os.path.splitext(value.name)[1].lower()
        valid_extensions = [".mp4", ".flv", ".avi"]
        if video_type_by_name not in valid_extensions:
            raise serializers.ValidationError(
                "Invalid video format. Only MP4, FLV, and AVI are allowed."
            )
        return value

    def create(self, validated_data):
        image_file = validated_data.pop("image", None)
        video_file = validated_data.pop("video", None)
        text = validated_data.pop("text", None)
        content_type = validated_data.pop("content_type", None)
        object_id = validated_data.pop("object_id", None)

        custom_post = CustomPost.objects.create(**validated_data)

        if image_file is not None:
            ImageAttachment.objects.create(content_object=custom_post, image=image_file)
        elif video_file is not None:
            VideoAttachment.objects.create(content_object=custom_post, video=video_file)
        elif text is not None:
            TextAttachment.objects.create(content_object=custom_post, text=text)

        if content_type and object_id:
            # Get the ContentType object for the given content_type
            try:
                content_type_obj = ContentType.objects.get(model=content_type.model)
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(
                    "Invalid content type. No model matches the given content type."
                )

            # Retrieve the MatchPost
            try:
                match_post = content_type_obj.get_object_for_this_type(pk=object_id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    "The referenced object does not exist."
                )

            # Associate the MatchPost with the CustomPost
            custom_post.content_type = content_type_obj
            custom_post.object_id = match_post.id
            custom_post.save()
        return custom_post

    def get_content_object(self, obj):
        if isinstance(obj.content_object, MatchPost):
            return MatchPostSerializer(obj.content_object).data
        return None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"].parsers = [MultiPartParser(), FormParser()]
        return context


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content")
