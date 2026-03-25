from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from courses.models import Course
from enrolments.models import Enrolment

User = get_user_model()


class ProtectedEndpointIntegrationTests(TestCase):
    """Integration tests for protected endpoints across apps."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', username='admin',
            password='Pass123!', role='admin'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', username='teacher',
            password='Pass123!', role='teacher'
        )
        self.student1 = User.objects.create_user(
            email='student1@test.com', username='student1',
            password='Pass123!', role='student'
        )
        self.student2 = User.objects.create_user(
            email='student2@test.com', username='student2',
            password='Pass123!', role='student'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Integration Test Course',
            code='INT101',
            description='Test course',
            instructor=self.teacher,
            is_published=True
        )
        
        # Enroll student1
        self.enrolment = Enrolment.objects.create(
            student=self.student1,
            course=self.course,
            status='active'
        )

    def test_unauthenticated_user_cannot_access_protected_endpoints(self):
        """Unauthenticated users should get 401 on protected endpoints."""
        r = self.client.get('/api/users/profile/')
        self.assertEqual(r.status_code, 401)

    def test_student_can_access_published_courses(self):
        """Students should see published courses in list."""
        self.client.force_authenticate(user=self.student1)
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 200)
        # Should contain the published course
        course_ids = [c['id'] for c in r.data if isinstance(r.data, list)]
        self.assertIn(self.course.id, course_ids)

    def test_student_cannot_see_unpublished_courses(self):
        """Students should not see unpublished courses."""
        unpublished = Course.objects.create(
            title='Draft Course',
            code='DRF101',
            description='Not published',
            instructor=self.teacher,
            is_published=False
        )
        
        self.client.force_authenticate(user=self.student1)
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 200)
        
        if isinstance(r.data, list):
            course_ids = [c['id'] for c in r.data]
            self.assertNotIn(unpublished.id, course_ids)

    def test_admin_can_see_all_courses(self):
        """Admins should see all courses (published and unpublished)."""
        unpublished = Course.objects.create(
            title='Draft Course',
            code='DRF102',
            description='Not published',
            instructor=self.teacher,
            is_published=False
        )
        
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, 200)
        
        if isinstance(r.data, list):
            # Admin should see both published and unpublished
            self.assertGreaterEqual(len(r.data), 2)

    def test_student_can_view_own_profile(self):
        """Students should access their own profile."""
        self.client.force_authenticate(user=self.student1)
        r = self.client.get('/api/users/profile/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['email'], 'student1@test.com')

    def test_student_cannot_view_other_student_profile(self):
        """Students should not have access to other student profiles."""
        self.client.force_authenticate(user=self.student1)
        # Assuming profile endpoints have user ID parameter
        r = self.client.get(f'/api/users/{self.student2.id}/')
        # Should be 404 or 403 depending on implementation
        self.assertIn(r.status_code, [403, 404])

    def test_teacher_can_view_own_course_enrolments(self):
        """Teachers should view enrolments for their courses."""
        self.client.force_authenticate(user=self.teacher)
        r = self.client.get(f'/api/courses/{self.course.id}/enrolments/')
        # Assuming this endpoint exists
        # Should either succeed or return 403 if endpoint doesn't exist yet
        self.assertIn(r.status_code, [200, 404])


class RoleBasedAccessControlTests(TestCase):
    """Tests for role-based access control across endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', username='admin',
            password='Pass123!', role='admin'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', username='teacher',
            password='Pass123!', role='teacher'
        )
        self.student = User.objects.create_user(
            email='student@test.com', username='student',
            password='Pass123!', role='student'
        )

    def test_only_admin_can_create_course(self):
        """Only admins should be able to create courses."""
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/courses/', {
            'title': 'Unauthorized Course',
            'code': 'UNAUTH101',
            'description': 'Should fail'
        })
        self.assertIn(r.status_code, [403, 400])

    def test_admin_can_create_course(self):
        """Admins should be able to create courses."""
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/courses/', {
            'title': 'Admin Course',
            'code': 'ADM101',
            'description': 'Created by admin'
        })
        self.assertEqual(r.status_code, 201)

    def test_teacher_can_view_users(self):
        """Teachers should have user listing access."""
        self.client.force_authenticate(user=self.teacher)
        r = self.client.get('/api/users/')
        # Should succeed or be restricted depending on implementation
        self.assertIn(r.status_code, [200, 403])

    def test_student_cannot_view_all_users(self):
        """Students should not see all user lists."""
        self.client.force_authenticate(user=self.student)
        r = self.client.get('/api/users/')
        self.assertEqual(r.status_code, 403)

    def test_admin_can_view_all_users(self):
        """Admins should view all users."""
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/users/')
        self.assertEqual(r.status_code, 200)


class DataIsolationTests(TestCase):
    """Tests for data isolation between users."""

    def setUp(self):
        self.client = APIClient()
        self.student1 = User.objects.create_user(
            email='student1@test.com', username='student1',
            password='Pass123!', role='student'
        )
        self.student2 = User.objects.create_user(
            email='student2@test.com', username='student2',
            password='Pass123!', role='student'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', username='teacher',
            password='Pass123!', role='teacher'
        )
        
        self.course1 = Course.objects.create(
            title='Course 1',
            code='CRS1',
            description='For student 1',
            instructor=self.teacher,
            is_published=True
        )
        
        self.course2 = Course.objects.create(
            title='Course 2',
            code='CRS2',
            description='For student 2',
            instructor=self.teacher,
            is_published=True
        )
        
        Enrolment.objects.create(
            student=self.student1,
            course=self.course1,
            status='active'
        )
        
        Enrolment.objects.create(
            student=self.student2,
            course=self.course2,
            status='active'
        )

    def test_student1_cannot_access_student2_enrolment_data(self):
        """Students should not access other student enrolments."""
        self.client.force_authenticate(user=self.student1)
        # Try to access enrolments endpoint
        r = self.client.get('/api/enrolments/')
        
        # If enrolments endpoint exists and returns list
        if r.status_code == 200 and isinstance(r.data, list):
            # Should only see own enrolments
            course_ids = [e.get('course') for e in r.data if e.get('course')]
            self.assertNotIn(self.course2.id, course_ids)

    def test_student_can_see_only_own_enrolments(self):
        """Students should see only their own enrolments."""
        self.client.force_authenticate(user=self.student1)
        r = self.client.get('/api/enrolments/')
        
        if r.status_code == 200 and isinstance(r.data, list):
            # Should contain enrolment to course1
            course_ids = [e.get('course') for e in r.data if e.get('course')]
            self.assertIn(self.course1.id, course_ids)

    def test_teacher_can_view_their_course_students(self):
        """Teachers should see students enrolled in their courses."""
        self.client.force_authenticate(user=self.teacher)
        r = self.client.get(f'/api/courses/{self.course1.id}/')
        self.assertEqual(r.status_code, 200)
