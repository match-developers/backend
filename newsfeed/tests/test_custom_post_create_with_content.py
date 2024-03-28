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

    def test_create_custom_post_with_image_and_video_then_fail(self):
        # Create a temporary image file
        img = Image.new("RGB", (60, 30), color=(73, 109, 137))
        file = io.BytesIO()
        img.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        image = SimpleUploadedFile(file.name, file.read(), content_type="image/png")

        # Create a temporary video file
        video = io.BytesIO(b"test video")
        video.name = "test.mp4"
        video.seek(0)

        # Create the data dictionary
        data = {
            "user": self.user.id,
            "title": "Test Post",
            "image": image,
            "video": video,
        }

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "A post can have either an image, a video, or text, but not multiple.",
        )

    def test_create_custom_post_with_image_and_text_then_fail(self):
        # Create a temporary image file
        img = Image.new("RGB", (60, 30), color=(73, 109, 137))
        file = io.BytesIO()
        img.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        image = SimpleUploadedFile(file.name, file.read(), content_type="image/png")

        # Create the data dictionary
        data = {
            "user": self.user.id,
            "title": "Test Post",
            "image": image,
            "text": "This is a test post.",
        }

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "A post can have either an image, a video, or text, but not multiple.",
        )

    def test_create_custom_post_with_video_and_text_then_fail(self):
        # Create a temporary video file
        video = io.BytesIO(b"test video")
        video.name = "test.mp4"
        video.seek(0)

        # Create the data dictionary
        data = {
            "user": self.user.id,
            "title": "Test Post",
            "video": video,
            "text": "This is a test post.",
        }

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "A post can have either an image, a video, or text, but not multiple.",
        )

    def test_create_custom_post_without_image_video_text_then_fail(self):
        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post"}

        # Send the POST request
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "A post must have either an image, a video, or text.",
        )

    def test_create_custom_post_without_title_then_fail(self):
        # Create the data dictionary
        data = {"user": self.user.id}

        # Send the POST request
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["title"][0],
            "This field is required.",
        )

    def test_create_custom_post_without_user_then_fail(self):
        # Create the data dictionary
        data = {"title": "Test Post"}

        # Send the POST request
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["user"][0],
            "This field is required.",
        )

    def test_create_custom_post_with_invalid_user_then_fail(self):
        # Create the data dictionary
        data = {"user": 999, "title": "Test Post"}

        # Send the POST request
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["user"][0],
            'Invalid pk "999" - object does not exist.',
        )

    def test_create_custom_post_with_invalid_image_then_fail(self):
        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post", "image": "invalid"}

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["image"][0],
            "The submitted data was not a file. Check the encoding type on the form.",
        )

    def test_create_custom_post_with_invalid_video_then_fail(self):
        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post", "video": "invalid"}

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["video"][0],
            "The submitted data was not a file. Check the encoding type on the form.",
        )

    def test_create_custom_post_with_invalid_image_extension_then_fail(self):
        # Create a temporary image file
        img = Image.new("RGB", (60, 30), color=(73, 109, 137))
        file = io.BytesIO()
        img.save(file, "png")
        file.name = "test.jpg"
        file.seek(0)
        image = SimpleUploadedFile(file.name, file.read(), content_type="image/png")

        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post", "image": image}

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["image"][0],
            "File extension does not match image format.",
        )

    def test_create_custom_post_with_invalid_video_extension_then_fail(self):
        # Create a temporary video file
        video = io.BytesIO(b"test video")
        video.name = "test.txt"
        video.seek(0)

        # Create the data dictionary
        data = {"user": self.user.id, "title": "Test Post", "video": video}

        # Send the POST request
        response = self.client.post(self.create_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["video"][0],
            "Invalid video format. Only MP4, FLV, and AVI are allowed.",
        )
