from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from . import models
from django.contrib.auth import get_user_model
from . import utils

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