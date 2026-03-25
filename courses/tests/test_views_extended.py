from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from datetime import date, timedelta

User = get_user_model()


class CourseListAPITests(TestCase):
    """Tests for course listing endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', username='admin',
            password='Pass123!', role='admin', is_admin=True
        )
        self.student = User.objects.create_user(
            email='student@test.com', username='student',
            password='Pass123!', role='student'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', username='teacher',
            password='Pass123!', role='teacher'
        )
        # Create published course
        self.published_course = Course.objects.create(
            title='Arabic A1', description='Beginner level',
            level='A1', status='published', pass_mark=60
        )
        # Create draft course
        self.draft_course = Course.objects.create(
            title='Arabic B1', description='Intermediate level',
            level='B1', status='draft', pass_mark=70
        )

    def test_unauthenticated_cannot_list_courses(self):
        """Unauthenticated users should not be able to list courses."""
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 401)

    def test_student_can_list_published_courses(self):
        """Students should only see published courses."""
        self.client.force_authenticate(user=self.student)
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['title'], 'Arabic A1')

    def test_teacher_can_list_published_courses(self):
        """Teachers should only see published courses."""
        self.client.force_authenticate(user=self.teacher)
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_admin_can_see_all_courses(self):
        """Admins should see both published and draft courses."""
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)

    def test_student_cannot_create_course(self):
        """Students should not be able to create courses."""
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/courses/', {
            'title': 'New Course', 'description': 'test',
            'level': 'A1', 'status': 'published', 'pass_mark': 60
        })
        self.assertEqual(r.status_code, 403)

    def test_admin_can_create_course(self):
        """Admins should be able to create courses."""
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/courses/', {
            'title': 'New Course', 'description': 'test',
            'level': 'C1', 'status': 'published', 'pass_mark': 75
        })
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['title'], 'New Course')


class CourseDetailAPITests(TestCase):
    """Tests for course detail endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', username='admin',
            password='Pass123!', role='admin', is_admin=True
        )
        self.student = User.objects.create_user(
            email='student@test.com', username='student',
            password='Pass123!', role='student'
        )
        self.published_course = Course.objects.create(
            title='Arabic A1', description='Beginner',
            level='A1', status='published', pass_mark=60
        )

    def test_unauthenticated_cannot_retrieve_course(self):
        """Unauthenticated users cannot retrieve course details."""
        r = self.client.get(f'/api/courses/{self.published_course.id}/')
        self.assertEqual(r.status_code, 401)

    def test_student_can_retrieve_published_course(self):
        """Students can retrieve published course details."""
        self.client.force_authenticate(user=self.student)
        r = self.client.get(f'/api/courses/{self.published_course.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['title'], 'Arabic A1')

    def test_student_cannot_update_course(self):
        """Students should not be able to update courses."""
        self.client.force_authenticate(user=self.student)
        r = self.client.patch(f'/api/courses/{self.published_course.id}/', {
            'title': 'Updated Title'
        })
        self.assertEqual(r.status_code, 403)

    def test_admin_can_update_course(self):
        """Admins should be able to update courses."""
        self.client.force_authenticate(user=self.admin)
        r = self.client.patch(f'/api/courses/{self.published_course.id}/', {
            'title': 'Updated Title'
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['title'], 'Updated Title')

    def test_student_cannot_delete_course(self):
        """Students should not be able to delete courses."""
        self.client.force_authenticate(user=self.student)
        r = self.client.delete(f'/api/courses/{self.published_course.id}/')
        self.assertEqual(r.status_code, 403)

    def test_admin_can_delete_course(self):
        """Admins should be able to delete courses."""
        self.client.force_authenticate(user=self.admin)
        r = self.client.delete(f'/api/courses/{self.published_course.id}/')
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Course.objects.filter(id=self.published_course.id).exists())
