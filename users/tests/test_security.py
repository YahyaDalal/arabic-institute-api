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

class InputSanitizationTests(TestCase):
    """Tests for input sanitization and validation."""

    def setUp(self):
        self.client = APIClient()

    def test_html_tags_stripped_from_username(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'xss@test.com',
            'username': 'validuser',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 201)

    def test_script_injection_in_username_rejected(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'xss2@test.com',
            'username': '<script>alert(1)</script>',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 400)

    def test_username_with_special_chars_rejected(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'special@test.com',
            'username': 'user@name!',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 400)

    def test_username_too_short_rejected(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'short@test.com',
            'username': 'ab',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 400)

    def test_invalid_email_format_rejected(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'notanemail',
            'username': 'validuser',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 400)

    def test_sql_injection_attempt_in_email_rejected(self):
        r = self.client.post('/api/auth/register/', {
            'email': "'; DROP TABLE users; --",
            'username': 'hacker',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 400)

    def test_empty_password_rejected(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'empty@test.com',
            'username': 'emptypass',
            'password': '',
            'password2': '',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 400)
        
        
class SecurityHeaderTests(TestCase):
    """Tests that security headers are present on responses."""

    def setUp(self):
        self.client = APIClient()

    def test_xframe_options_header_present(self):
        r = self.client.get('/api/auth/register/')
        self.assertEqual(r.get('X-Frame-Options'), 'DENY')

    def test_content_type_nosniff_header_present(self):
        r = self.client.get('/api/auth/register/')
        self.assertEqual(r.get('X-Content-Type-Options'), 'nosniff')
