from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class TokenBlacklistTests(TestCase):
    """Tests for JWT token blacklisting on logout."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='logout@test.com', username='logoutuser',
            password='Pass123!'
        )

    def get_tokens(self):
        r = self.client.post('/api/auth/login/', {
            'email': 'logout@test.com',
            'password': 'Pass123!'
        })
        return r.data['access'], r.data['refresh']

    def test_logout_with_valid_refresh_token(self):
        access, refresh = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        r = self.client.post('/api/auth/logout/', {'refresh': refresh})
        self.assertEqual(r.status_code, 200)

    def test_logout_without_refresh_token_fails(self):
        access, _ = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        r = self.client.post('/api/auth/logout/', {})
        self.assertEqual(r.status_code, 400)

    def test_logout_with_invalid_refresh_token_fails(self):
        access, _ = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        r = self.client.post('/api/auth/logout/', {'refresh': 'invalidtoken'})
        self.assertEqual(r.status_code, 400)

    def test_blacklisted_refresh_token_cannot_be_reused(self):
        access, refresh = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        # Logout — blacklists the refresh token
        self.client.post('/api/auth/logout/', {'refresh': refresh})
        # Try to use the blacklisted refresh token
        r = self.client.post('/api/auth/token/refresh/', {'refresh': refresh})
        self.assertEqual(r.status_code, 401)

    def test_logout_requires_authentication(self):
        r = self.client.post('/api/auth/logout/', {'refresh': 'sometoken'})
        self.assertEqual(r.status_code, 401)

