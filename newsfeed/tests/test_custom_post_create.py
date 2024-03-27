import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from accounts.tests.factories import AccountFactory
from newsfeed.models import CustomPost, ImageAttachment, TextAttachment, VideoAttachment


class CustomPostCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = AccountFactory()
        self.client.force_authenticate(self.user)
        self.create_url = reverse("custom_posts")

    def test_create_custom_post_with_image_att_then_success(self):
        # Create a temporary image file
        img = Image.new("RGB", (60, 30), color=(73, 109, 137))
        file = io.BytesIO()
        img.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        image = SimpleUploadedFile(file.name, file.read(), content_type="image/png")

        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post", "image": image}

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Post")
        self.assertEqual(response.data["user"], self.user.id)

        # Verify that an ImageAttachment object was created
        self.assertTrue(ImageAttachment.objects.exists())

        # Retrieve the created CustomPost object
        custom_post = CustomPost.objects.get(title="Test Post")

        # Verify that an ImageAttachment object is associated with the CustomPost
        self.assertTrue(custom_post.images.exists())

    def test_create_custom_post_with_video_att_then_success(self):
        # Create a temporary video file
        video = io.BytesIO(b"test video")
        video.name = "test.mp4"
        video.seek(0)

        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post", "video": video}

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Post")
        self.assertEqual(response.data["user"], self.user.id)

        # Verify that a VideoAttachment object was created
        self.assertTrue(VideoAttachment.objects.exists())

        # Retrieve the created CustomPost object
        custom_post = CustomPost.objects.get(title="Test Post")

        # Verify that a VideoAttachment object is associated with the CustomPost
        self.assertTrue(custom_post.videos.exists())

    def test_create_custom_post_with_text_att_then_success(self):
        # Create the data dictionary
        data = {
            "user": self.user.id,
            "title": "Test Post",
            "text": "This is a test post.",
        }

        # Send the POST request
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Post")
        self.assertEqual(response.data["user"], self.user.id)

        self.assertTrue(TextAttachment.objects.exists())

        custom_post = CustomPost.objects.get(title="Test Post")

        self.assertTrue(custom_post.texts.exists())
