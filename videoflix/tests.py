from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from . import models
from django.contrib.auth import get_user_model
from . import utils
from datetime import datetime
from .views import TOKEN_EXPIRY_DURATION
from . import tasks
import os
from django.conf import settings


# Create your tests here.

def get_authenticated_client():
    user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token  {token.key}")
    return client

class CheckEmailTestCase(APITestCase):
    def test_email_exists_not(self):
        client = APIClient()
        response = client.post(
            "/api/check-email/",
            {
                "email": "test@test.de"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_inactive_email_exists(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        client = APIClient()
        response = client.post(
            "/api/check-email/",
            {
                "email": "test@test.de"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_active_email_exists(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        user.is_active = True
        user.save()
        client = APIClient()
        response = client.post(
            "/api/check-email/",
            {
                "email": "test@test.de"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 200)

class CheckSignupTestCase(APITestCase):
    def test_unavailable_email(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        client = APIClient()
        response = client.post(
            "/api/signup/",
            {
                "email": "test@test.de",
                "password": "aBcD98!?"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_available_email(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        client = APIClient()
        response = client.post(
            "/api/signup/",
            {
                "email": "another_test@test.de",
                "password": "aBcD98!?"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 201)

class ActivateUserTestCase(APITestCase):
    def test_with_valid_token(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        activation_token = utils.create_token(user.email)
        client = APIClient()
        response = client.put(
            "/api/activate/",
            {
                "activationtoken": activation_token
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user_model().objects.filter(email=user.email, is_active=True).exists(), True)

    def test_with_invalid_token(self):
        invalid_token = utils.create_token("invalid")
        client = APIClient()
        response = client.put(
            "/api/activate/",
            {
                "activationtoken": invalid_token
            }
        )
        self.assertEqual(response.status_code, 400)

class LoginTestCase(APITestCase):
    def test_inactive_user(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        client = APIClient()
        response = client.post(
            "/api/login/",
            {
                "email": user.email,
                "password": "aBcD98!?"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_active_user_with_valid_credentials(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        user.is_active = True
        user.save()
        client = APIClient()
        response = client.post(
            "/api/login/",
            {
                "email": user.email,
                "password": "aBcD98!?"
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_with_invalid_credentials(self):
        client = APIClient()
        response = client.post(
            "/api/login/",
            {
                "email": "test",
                "password": "test"
            }
        )
        self.assertEqual(response.status_code, 400)

class RequestPasswordResetTestCase(APITestCase):
    def test_inactive_user(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        client = APIClient()
        response = client.post(
            "/api/request-password-reset/",
            {
                "email": user.email
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_active_user(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        user.is_active = True
        user.save()
        client = APIClient()
        response = client.post(
            "/api/request-password-reset/",
            {
                "email": user.email
            }
        )
        self.assertEqual(response.status_code, 200)

class ResetPasswordTestCase(APITestCase):
    def test_with_valid_token(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        Token.objects.get_or_create(user=user)
        token = utils.create_token(user.email, int(datetime.now().timestamp() + TOKEN_EXPIRY_DURATION))
        client = APIClient()
        response = client.post(
            f"/api/reset-password/{token}/",
            {"password": "aBcD98!?"}
        )
        self.assertEqual(response.status_code, 200)
        
    def test_with_expired_token(self):
        user = get_user_model().objects.create_user(email="test@test.de", password="aBcD98!?")
        token = utils.create_token(user.email, int(datetime.now().timestamp() - TOKEN_EXPIRY_DURATION))
        client = APIClient()
        response = client.post(
            f"/api/reset-password/{token}/",
            {"password": "aBcD98!?"}
        )
        self.assertEqual(response.status_code, 400)

class CreatePosterTestCase(TestCase):
    def test_create_poster(self):
        #category = models.VideoCategory.objects.create(title="Test category")
        video = models.Video.objects.create(title="Test", description="Test", featured=False)
        #video.categories.add(category)
        tasks.create_video_poster("/django/test-data/sample-video.mp4", video.id)
        self.assertEqual(os.path.isfile(os.path.join(settings.MEDIA_ROOT, "posters", f"{video.id}.jpg")), True)