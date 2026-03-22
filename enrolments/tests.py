from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from enrolments.models import Enrolment
from datetime import date

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        data = {
            'email': 'student@test.com',
            'username': 'student1',
            'password': 'Secure123!',
            'password2': 'Secure123!',
            'role': 'student'
        }
        r = self.client.post('/api/auth/register/', data)
        self.assertEqual(r.status_code, 201)

    def test_register_password_mismatch(self):
        data = {
            'email': 'student2@test.com',
            'username': 'student2',
            'password': 'Secure123!',
            'password2': 'Wrong123!',
            'role': 'student'
        }
        r = self.client.post('/api/auth/register/', data)
        self.assertEqual(r.status_code, 400)

    def test_login_success(self):
        User.objects.create_user(
            email='login@test.com', username='loginuser', password='Pass123!'
        )
        r = self.client.post('/api/auth/login/', {
            'email': 'login@test.com', 'password': 'Pass123!'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)

    def test_protected_endpoint_requires_auth(self):
        r = self.client.get('/api/enrolments/my/')
        self.assertEqual(r.status_code, 401)

    def test_profile_requires_auth(self):
        r = self.client.get('/api/auth/profile/')
        self.assertEqual(r.status_code, 401)

