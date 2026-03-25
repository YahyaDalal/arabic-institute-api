from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import secrets

User = get_user_model()


class PasswordResetAPITests(TestCase):
    """Tests for password reset endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='reset@test.com', username='resetuser',
            password='OldPass123!', role='student'
        )
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_password_reset_request_with_existing_email(self):
        """Password reset request should succeed for existing emails."""
        r = self.client.post('/api/auth/password-reset/', {
            'email': 'reset@test.com'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('message', r.data)

    def test_password_reset_request_with_nonexistent_email(self):
        """Password reset request should still return success (security)."""
        r = self.client.post('/api/auth/password-reset/', {
            'email': 'nonexistent@test.com'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('message', r.data)

    def test_password_reset_with_invalid_token(self):
        """Password reset with invalid token should fail."""
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'token': 'invalid_token_12345',
            'password': 'NewPass123!'
        })
        self.assertEqual(r.status_code, 400)
        self.assertIn('error', r.data)

    def test_password_reset_with_valid_token(self):
        """Password reset with valid token should succeed."""
        # Generate a valid token
        token = secrets.token_urlsafe(32)
        cache.set(f'pwd_reset_{token}', self.user.pk, timeout=3600)
        
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'token': token,
            'password': 'NewPass123!'
        })
        self.assertEqual(r.status_code, 200)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))

    def test_password_reset_token_expires(self):
        """Expired token should not work."""
        token = secrets.token_urlsafe(32)
        # Set very short timeout
        cache.set(f'pwd_reset_{token}', self.user.pk, timeout=1)
        
        # Simulate expiration
        cache.delete(f'pwd_reset_{token}')
        
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'token': token,
            'password': 'NewPass123!'
        })
        self.assertEqual(r.status_code, 400)


class LogoutAPITests(TestCase):
    """Tests for logout endpoint with token blacklisting."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='logout@test.com', username='logoutuser',
            password='Pass123!', role='student'
        )

    def test_logout_requires_authentication(self):
        """Logout should require authentication."""
        r = self.client.post('/api/auth/logout/', {'refresh': 'token'})
        self.assertEqual(r.status_code, 401)

    def test_logout_without_refresh_token(self):
        """Logout without refresh token should fail."""
        self.client.force_authenticate(user=self.user)
        r = self.client.post('/api/auth/logout/', {})
        self.assertEqual(r.status_code, 400)
        self.assertIn('error', r.data)

    def test_logout_with_valid_token(self):
        """Logout with valid refresh token should succeed."""
        self.client.force_authenticate(user=self.user)
        
        # Get tokens
        login_r = self.client.post('/api/auth/login/', {
            'email': 'logout@test.com',
            'password': 'Pass123!'
        })
        refresh_token = login_r.data['refresh']
        
        # Logout
        r = self.client.post('/api/auth/logout/', {'refresh': refresh_token})
        self.assertEqual(r.status_code, 200)
        self.assertIn('message', r.data)

    def test_logout_with_invalid_token(self):
        """Logout with invalid token should fail."""
        self.client.force_authenticate(user=self.user)
        r = self.client.post('/api/auth/logout/', {
            'refresh': 'invalid.token.here'
        })
        self.assertEqual(r.status_code, 400)
        self.assertIn('error', r.data)

    def test_cannot_reuse_blacklisted_token(self):
        """Blacklisted token should not be reusable."""
        self.client.force_authenticate(user=self.user)
        
        # Get tokens
        login_r = self.client.post('/api/auth/login/', {
            'email': 'logout@test.com',
            'password': 'Pass123!'
        })
        refresh_token = login_r.data['refresh']
        
        # Logout to blacklist token
        self.client.post('/api/auth/logout/', {'refresh': refresh_token})
        
        # Try to use old refresh token to get new access token
        r = self.client.post('/api/token/refresh/', {'refresh': refresh_token})
        # Should be blacklisted
        self.assertNotEqual(r.status_code, 200)
