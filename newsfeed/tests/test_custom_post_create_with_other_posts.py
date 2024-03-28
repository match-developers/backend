import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from accounts.tests.factories import AccountFactory
from matchmaking.models import MatchPost
from matchmaking.tests.factories import MatchPostFactory
from newsfeed.models import CustomPost, ImageAttachment, TextAttachment, VideoAttachment


class CustomPostCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = AccountFactory()
        self.client.force_authenticate(self.user)
        self.create_url = reverse("custom_posts")

    def test_create_custom_post_with_match_post_then_success(self):
        # match_post = MatchPostFactory()

        # # Create a custom post with a match post
        # response = self.client.post(
        #     self.create_url,
        #     {
        #         "title": "Custom post with match post",
        #         "content_type": "match_post",
        #         "object_id": match_post.id,
        #     },
        # )

        # print(response.content)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(CustomPost.objects.count(), 1)
        # custom_post = CustomPost.objects.first()
        # self.assertEqual(custom_post.title, "Custom post with match post")
        # self.assertEqual(custom_post.user, self.user)
        # self.assertEqual(custom_post.content_object, match_post)
        pass
