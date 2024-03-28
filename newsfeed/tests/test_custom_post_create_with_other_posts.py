from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from accounts.tests.factories import AccountFactory
from matchmaking.models import MatchPost
from matchmaking.tests.factories import MatchFactory, MatchPostFactory
from newsfeed.models import CustomPost


class CustomPostCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = AccountFactory()
        self.client.force_authenticate(self.user)
        self.create_url = reverse("custom_posts")

    def test_create_custom_post_with_match_post_then_success(self):
        match = MatchFactory(
            is_club=True,
            match_type="friendly",
        )
        match_post = MatchPostFactory(match=match)
        match_post_content_type = ContentType.objects.get_for_model(MatchPost)

        # Create a custom post with a match post
        response = self.client.post(
            self.create_url,
            {
                "user": self.user.id,
                "title": "Custom post with match post",
                "content_type": "matchpost",
                "object_id": match_post.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content_type"], match_post_content_type.model)
        self.assertEqual(response.data["object_id"], match_post.id)
        self.assertEqual(response.data["content_object"]["title"], match_post.title)

        match_post = MatchPost.objects.get(id=match_post.id)
        custom_post = CustomPost.objects.get(id=response.data["id"])

        self.assertEqual(custom_post.content_object, match_post)
