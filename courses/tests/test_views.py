from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from enrolments.models import Enrolment
from datetime import date, timedelta

User = get_user_model()


class EnrolmentAPITests(TestCase):
    """Integration tests for enrolment API endpoints."""

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
        self.course = Course.objects.create(
            title='Arabic A1', description='x',
            level='A1', status='published', pass_mark=60
        )
        self.cohort = Cohort.objects.create(
            course=self.course, teacher=self.teacher,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            capacity=5, enrolment_open=True
        )

    def test_student_can_enrol(self):
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': self.cohort.id})
        self.assertEqual(r.status_code, 201)

    def test_enrolment_response_contains_expected_fields(self):
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/enrolments/', {'cohort': self.cohort.id})
        self.assertIn('cohort', r.data)
        self.assertIn('course_title', r.data)
        self.assertIn('final_grade', r.data)
        self.assertIn('fees_paid', r.data)

    def test_teacher_can_update_grade(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort, status='active'
        )
        self.client.force_authenticate(user=self.teacher)
        r = self.client.patch(f'/api/enrolments/{enrolment.id}/', {
            'attendance_percentage': 85,
            'final_grade': 72,
            'fees_paid': True,
            'teacher_approved': True,
        })
        self.assertEqual(r.status_code, 200)
        enrolment.refresh_from_db()
        self.assertEqual(enrolment.status, 'completed')

    def test_student_withdrawal_changes_status(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort, status='active'
        )
        self.client.force_authenticate(user=self.student)
        r = self.client.patch(f'/api/enrolments/{enrolment.id}/withdraw/')
        self.assertEqual(r.status_code, 200)
        enrolment.refresh_from_db()
        self.assertEqual(enrolment.status, 'withdrawn')