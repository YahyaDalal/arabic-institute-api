from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from enrolments.models import Enrolment
from certificates.models import Certificate
from datetime import date, timedelta

User = get_user_model()


class CertificateAPITests(TestCase):
    """Integration tests for certificate API endpoints."""

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
            capacity=10, enrolment_open=True
        )
        self.eligible_enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='completed', attendance_percentage=80,
            final_grade=75, fees_paid=True, teacher_approved=True
        )

    def test_teacher_can_issue_certificate(self):
        self.client.force_authenticate(user=self.teacher)
        r = self.client.post('/api/certificates/', {
            'enrolment': self.eligible_enrolment.id
        })
        self.assertEqual(r.status_code, 201)

    def test_student_cannot_issue_certificate(self):
        self.client.force_authenticate(user=self.student)
        r = self.client.post('/api/certificates/', {
            'enrolment': self.eligible_enrolment.id
        })
        self.assertEqual(r.status_code, 403)

    def test_cannot_issue_duplicate_certificate(self):
        Certificate.objects.create(
            enrolment=self.eligible_enrolment, issued_by=self.teacher
        )
        self.client.force_authenticate(user=self.teacher)
        r = self.client.post('/api/certificates/', {
            'enrolment': self.eligible_enrolment.id
        })
        self.assertEqual(r.status_code, 400)

    def test_student_can_view_own_certificates(self):
        Certificate.objects.create(
            enrolment=self.eligible_enrolment, issued_by=self.teacher
        )
        self.client.force_authenticate(user=self.student)
        r = self.client.get('/api/certificates/my/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_student_cannot_view_all_certificates(self):
        self.client.force_authenticate(user=self.student)
        r = self.client.get('/api/certificates/all/')
        self.assertEqual(r.status_code, 403)

    def test_ineligible_enrolment_cannot_get_certificate(self):
        ineligible = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='active', attendance_percentage=50,
            final_grade=30, fees_paid=False, teacher_approved=False
        )
        self.client.force_authenticate(user=self.teacher)
        r = self.client.post('/api/certificates/', {'enrolment': ineligible.id})
        self.assertEqual(r.status_code, 400)