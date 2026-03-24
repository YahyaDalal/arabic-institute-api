from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthAPITests(TestCase):
    """Integration tests for authentication endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_register_returns_201(self):
        r = self.client.post('/api/auth/register/', {
            'email': 'new@test.com', 'username': 'newuser',
            'password': 'Pass123!', 'password2': 'Pass123!', 'role': 'student'
        })
        self.assertEqual(r.status_code, 201)

    def test_login_returns_jwt_tokens(self):
        User.objects.create_user(email='login@test.com', username='loginuser', password='Pass123!')
        r = self.client.post('/api/auth/login/', {
            'email': 'login@test.com', 'password': 'Pass123!'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_profile_requires_authentication(self):
        r = self.client.get('/api/auth/profile/')
        self.assertEqual(r.status_code, 401)

    def test_authenticated_user_can_get_profile(self):
        user = User.objects.create_user(
            email='me@test.com', username='me', password='Pass123!'
        )
        self.client.force_authenticate(user=user)
        r = self.client.get('/api/auth/profile/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['email'], 'me@test.com')

    def test_duplicate_email_registration_fails(self):
        User.objects.create_user(email='dup@test.com', username='dup', password='Pass123!')
        r = self.client.post('/api/auth/register/', {
            'email': 'dup@test.com', 'username': 'dup2',
            'password': 'Pass123!', 'password2': 'Pass123!', 'role': 'student'
        })
        self.assertEqual(r.status_code, 400)

    def test_cannot_change_role_via_profile_patch(self):
        user = User.objects.create_user(
            email='norole@test.com', username='norole',
            password='Pass123!', role='student'
        )
        self.client.force_authenticate(user=user)
        r = self.client.patch('/api/auth/profile/', {'role': 'admin'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['role'], 'student')