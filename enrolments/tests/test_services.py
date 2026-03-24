from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from enrolments.models import Enrolment
from datetime import date, timedelta

User = get_user_model()


class EnrolmentStatusServiceTests(TestCase):
    """
    Unit tests for the update_status() service method.
    These test business logic in complete isolation from HTTP.
    """

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
        self.enrolment = Enrolment.objects.create(
            student=self.student, cohort=self.cohort, status='active'
        )

    def test_update_status_completed_when_passing(self):
        self.enrolment.attendance_percentage = 80
        self.enrolment.final_grade = 70
        self.enrolment.update_status()
        self.assertEqual(self.enrolment.status, 'completed')

    def test_update_status_failed_when_grade_below_pass_mark(self):
        self.enrolment.attendance_percentage = 90
        self.enrolment.final_grade = 50
        self.enrolment.update_status()
        self.assertEqual(self.enrolment.status, 'failed')

    def test_update_status_failed_when_attendance_below_75(self):
        self.enrolment.attendance_percentage = 74
        self.enrolment.final_grade = 90
        self.enrolment.update_status()
        self.assertEqual(self.enrolment.status, 'failed')

    def test_update_status_does_nothing_without_grade(self):
        self.enrolment.attendance_percentage = 90
        self.enrolment.final_grade = None
        self.enrolment.update_status()
        self.assertEqual(self.enrolment.status, 'active')

    def test_update_status_boundary_attendance_exactly_75(self):
        self.enrolment.attendance_percentage = 75
        self.enrolment.final_grade = 70
        self.enrolment.update_status()
        self.assertEqual(self.enrolment.status, 'completed')

    def test_update_status_boundary_grade_exactly_at_pass_mark(self):
        self.enrolment.attendance_percentage = 80
        self.enrolment.final_grade = 60  # Exactly at pass_mark
        self.enrolment.update_status()
        self.assertEqual(self.enrolment.status, 'completed')


class CertificateEligibilityTests(TestCase):
    """
    Unit tests for the can_issue_certificate property.
    Tests every possible combination of failing criteria.
    """

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

    def make_enrolment(self, **kwargs):
        defaults = {
            'student': self.student,
            'cohort': self.cohort,
            'status': 'completed',
            'attendance_percentage': 80,
            'final_grade': 75,
            'fees_paid': True,
            'teacher_approved': True,
        }
        defaults.update(kwargs)
        return Enrolment(**defaults)

    def test_all_criteria_met_returns_true(self):
        self.assertTrue(self.make_enrolment().can_issue_certificate)

    def test_fails_if_status_not_completed(self):
        self.assertFalse(self.make_enrolment(status='active').can_issue_certificate)

    def test_fails_if_grade_below_pass_mark(self):
        self.assertFalse(self.make_enrolment(final_grade=30).can_issue_certificate)

    def test_fails_if_grade_is_none(self):
        self.assertFalse(self.make_enrolment(final_grade=None).can_issue_certificate)

    def test_fails_if_attendance_below_75(self):
        self.assertFalse(self.make_enrolment(attendance_percentage=74).can_issue_certificate)

    def test_fails_if_fees_not_paid(self):
        self.assertFalse(self.make_enrolment(fees_paid=False).can_issue_certificate)

    def test_fails_if_teacher_not_approved(self):
        self.assertFalse(self.make_enrolment(teacher_approved=False).can_issue_certificate)

    def test_boundary_attendance_exactly_75_passes(self):
        self.assertTrue(self.make_enrolment(attendance_percentage=75).can_issue_certificate)

    def test_boundary_grade_exactly_at_pass_mark_passes(self):
        self.assertTrue(self.make_enrolment(final_grade=60).can_issue_certificate)

    def test_boundary_grade_one_below_pass_mark_fails(self):
        self.assertFalse(self.make_enrolment(final_grade=59).can_issue_certificate)