from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelUnitTests(TestCase):
    """Unit tests for the User model properties and methods."""

    def setUp(self):
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

    def test_is_student_property_true_for_student(self):
        self.assertTrue(self.student.is_student)

    def test_is_student_property_false_for_teacher(self):
        self.assertFalse(self.teacher.is_student)

    def test_is_teacher_property_true_for_teacher(self):
        self.assertTrue(self.teacher.is_teacher)

    def test_is_admin_property_true_for_admin(self):
        self.assertTrue(self.admin.is_admin)

    def test_str_representation(self):
        self.assertEqual(str(self.student), 'student@test.com (student)')

    def test_email_is_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='student@test.com', username='stu2',
                password='Pass123!', role='student'
            )

    def test_default_role_is_student(self):
        user = User.objects.create_user(
            email='default@test.com', username='def',
            password='Pass123!'
        )
        self.assertEqual(user.role, 'student')

    def test_password_is_hashed(self):
        self.assertNotEqual(self.student.password, 'Pass123!')
        self.assertTrue(self.student.password.startswith('pbkdf2_'))