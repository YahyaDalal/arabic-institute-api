from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Cohort
from enrolments.models import Enrolment
from datetime import date, timedelta

User = get_user_model()


class CourseModelUnitTests(TestCase):
    """Unit tests for Course model logic."""

    def test_str_representation(self):
        course = Course.objects.create(
            title='Arabic A1', description='Beginner',
            level='A1', status='published', pass_mark=60
        )
        self.assertEqual(str(course), 'Arabic A1 (published)')

    def test_default_status_is_draft(self):
        course = Course.objects.create(
            title='Draft Course', description='x', level='A1'
        )
        self.assertEqual(course.status, 'draft')

    def test_default_pass_mark_is_60(self):
        course = Course.objects.create(
            title='Default Pass', description='x', level='A1'
        )
        self.assertEqual(course.pass_mark, 60)

    def test_prerequisites_many_to_many(self):
        course_a = Course.objects.create(title='A', description='x', level='A1', status='published')
        course_b = Course.objects.create(title='B', description='x', level='A2', status='published')
        course_b.prerequisites.add(course_a)
        self.assertIn(course_a, course_b.prerequisites.all())


class CohortModelUnitTests(TestCase):
    """Unit tests for Cohort model properties."""

    def setUp(self):
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
            capacity=3, enrolment_open=True
        )

    def test_is_full_false_when_below_capacity(self):
        self.assertFalse(self.cohort.is_full)

    def test_is_full_true_when_at_capacity(self):
        for i in range(3):
            s = User.objects.create_user(
                email=f's{i}@test.com', username=f's{i}', password='x'
            )
            Enrolment.objects.create(student=s, cohort=self.cohort, status='active')
        self.assertTrue(self.cohort.is_full)

    def test_withdrawn_enrolments_not_counted_in_capacity(self):
        student = User.objects.create_user(
            email='withdrawn@test.com', username='withdrawn', password='x'
        )
        Enrolment.objects.create(student=student, cohort=self.cohort, status='withdrawn')
        self.assertEqual(self.cohort.current_enrolment_count, 0)

    def test_current_enrolment_count_accurate(self):
        for i in range(2):
            s = User.objects.create_user(
                email=f'c{i}@test.com', username=f'c{i}', password='x'
            )
            Enrolment.objects.create(student=s, cohort=self.cohort, status='active')
        self.assertEqual(self.cohort.current_enrolment_count, 2)