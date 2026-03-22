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


class EnrolmentBusinessLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.student = User.objects.create_user(
            email='student@test.com', username='stu',
            password='Pass123!', role='student'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', username='teach',
            password='Pass123!', role='teacher'
        )
        self.admin = User.objects.create_user(
            email='admin@test.com', username='adm',
            password='Pass123!', role='admin'
        )
        self.course = Course.objects.create(
            title='Arabic A1', description='Beginner Arabic',
            level='A1', status='published', pass_mark=60
        )
        self.cohort = Cohort.objects.create(
            course=self.course,
            teacher=self.teacher,
            start_date=date.today(),
            end_date=date.today(),
            capacity=2,
            enrolment_open=True
        )

    def test_student_can_enrol(self):
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': self.cohort.pk})
        self.assertEqual(r.status_code, 201)

    def test_cannot_enrol_in_full_cohort(self):
        # Fill the cohort to capacity
        for i in range(2):
            s = User.objects.create_user(
                email=f'extra{i}@test.com', username=f'extra{i}',
                password='Pass123!', role='student'
            )
            Enrolment.objects.create(student=s, cohort=self.cohort, status='active')

        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': self.cohort.pk})
        self.assertEqual(r.status_code, 400)

    def test_cannot_enrol_in_unpublished_course(self):
        draft_course = Course.objects.create(
            title='Draft Course', description='Not published',
            level='A2', status='draft', pass_mark=60
        )
        draft_cohort = Cohort.objects.create(
            course=draft_course, teacher=self.teacher,
            start_date=date.today(), end_date=date.today(),
            capacity=10, enrolment_open=True
        )
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': draft_cohort.pk})
        self.assertEqual(r.status_code, 400)

    def test_cannot_enrol_when_enrolment_closed(self):
        self.cohort.enrolment_open = False
        self.cohort.save()
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': self.cohort.pk})
        self.assertEqual(r.status_code, 400)

    def test_cannot_enrol_without_prerequisite(self):
        prereq_course = Course.objects.create(
            title='Prerequisite', description='Must complete first',
            level='A0', status='published', pass_mark=60
        )
        self.course.prerequisites.add(prereq_course)
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': self.cohort.pk})
        self.assertEqual(r.status_code, 400)

    def test_certificate_criteria_not_met_if_grade_too_low(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='active', attendance_percentage=80,
            final_grade=30, fees_paid=True, teacher_approved=True
        )
        self.assertFalse(enrolment.can_issue_certificate)

    def test_certificate_criteria_not_met_if_attendance_low(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='completed', attendance_percentage=50,
            final_grade=80, fees_paid=True, teacher_approved=True
        )
        self.assertFalse(enrolment.can_issue_certificate)

    def test_certificate_criteria_not_met_if_fees_unpaid(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='completed', attendance_percentage=80,
            final_grade=80, fees_paid=False, teacher_approved=True
        )
        self.assertFalse(enrolment.can_issue_certificate)

    def test_certificate_criteria_met(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='completed', attendance_percentage=80,
            final_grade=75, fees_paid=True, teacher_approved=True
        )
        self.assertTrue(enrolment.can_issue_certificate)

    def test_teacher_cannot_access_admin_endpoints(self):
        self.client.force_authenticate(user=self.teacher)
        r = self.client.post('/api/courses/', {
            'title': 'Hack', 'description': 'x',
            'level': 'A1', 'status': 'published', 'pass_mark': 60
        })
        self.assertEqual(r.status_code, 403)

    def test_student_cannot_access_cohort_enrolments(self):
        self.client.force_authenticate(user=self.student)
        r = self.client.get(f'/api/enrolments/cohort/{self.cohort.pk}/')
        self.assertEqual(r.status_code, 403)