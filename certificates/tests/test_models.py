from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from enrolments.models import Enrolment
from certificates.models import Certificate
from datetime import date, timedelta

User = get_user_model()


class CertificateModelUnitTests(TestCase):
    """Unit tests for Certificate model validation."""

    def setUp(self):
        self.student = User.objects.create_user(
            email='student@test.com', username='stu', password='Pass123!'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', username='teach', password='Pass123!'
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

    def make_eligible_enrolment(self):
        return Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='completed', attendance_percentage=80,
            final_grade=75, fees_paid=True, teacher_approved=True
        )

    def test_certificate_clean_passes_when_eligible(self):
        enrolment = self.make_eligible_enrolment()
        cert = Certificate(enrolment=enrolment, issued_by=self.teacher)
        try:
            cert.clean()
        except ValidationError:
            self.fail('clean() raised ValidationError unexpectedly')

    def test_certificate_clean_fails_when_not_eligible(self):
        enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort,
            status='active', attendance_percentage=80,
            final_grade=30, fees_paid=False, teacher_approved=False
        )
        cert = Certificate(enrolment=enrolment, issued_by=self.teacher)
        with self.assertRaises(ValidationError):
            cert.clean()

    def test_certificate_str_representation(self):
        enrolment = self.make_eligible_enrolment()
        cert = Certificate.objects.create(enrolment=enrolment, issued_by=self.teacher)
        self.assertIn('student@test.com', str(cert))
        self.assertIn('Arabic A1', str(cert))

    def test_cannot_create_duplicate_certificate(self):
        enrolment = self.make_eligible_enrolment()
        Certificate.objects.create(enrolment=enrolment, issued_by=self.teacher)
        with self.assertRaises(Exception):
            Certificate.objects.create(enrolment=enrolment, issued_by=self.teacher)