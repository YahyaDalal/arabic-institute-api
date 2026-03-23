from django.test import TestCase
from django.contrib.auth import get_user_model
from users.serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()


class RegisterSerializerUnitTests(TestCase):
    """Unit tests for the RegisterSerializer validation logic."""

    def get_valid_data(self, **overrides):
        data = {
            'email': 'new@test.com',
            'username': 'newuser',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'student'
        }
        data.update(overrides)
        return data

    def test_valid_data_passes(self):
        s = RegisterSerializer(data=self.get_valid_data())
        self.assertTrue(s.is_valid())

    def test_password_mismatch_fails(self):
        s = RegisterSerializer(data=self.get_valid_data(password2='WrongPass123!'))
        self.assertFalse(s.is_valid())
        self.assertIn('password', s.errors)

    def test_weak_password_fails(self):
        s = RegisterSerializer(data=self.get_valid_data(password='123', password2='123'))
        self.assertFalse(s.is_valid())

    def test_invalid_email_fails(self):
        s = RegisterSerializer(data=self.get_valid_data(email='notanemail'))
        self.assertFalse(s.is_valid())

    def test_missing_email_fails(self):
        data = self.get_valid_data()
        del data['email']
        s = RegisterSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_create_user_hashes_password(self):
        s = RegisterSerializer(data=self.get_valid_data())
        self.assertTrue(s.is_valid())
        user = s.save()
        self.assertNotEqual(user.password, 'SecurePass123!')

    def test_password2_not_saved_to_user(self):
        s = RegisterSerializer(data=self.get_valid_data())
        self.assertTrue(s.is_valid())
        user = s.save()
        self.assertFalse(hasattr(user, 'password2'))


class UserProfileSerializerUnitTests(TestCase):
    """Unit tests for the UserProfileSerializer read-only field enforcement."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@test.com', username='profileuser',
            password='Pass123!', role='student'
        )

    def test_role_is_read_only(self):
        s = UserProfileSerializer(
            self.user,
            data={'username': 'updated', 'role': 'admin'},
            partial=True
        )
        self.assertTrue(s.is_valid())
        updated = s.save()
        self.assertEqual(updated.role, 'student')

    def test_email_is_read_only(self):
        s = UserProfileSerializer(
            self.user,
            data={'email': 'hacked@test.com'},
            partial=True
        )
        self.assertTrue(s.is_valid())
        updated = s.save()
        self.assertEqual(updated.email, 'profile@test.com')

    def test_bio_can_be_updated(self):
        s = UserProfileSerializer(
            self.user,
            data={'bio': 'I love Arabic!'},
            partial=True
        )
        self.assertTrue(s.is_valid())
        updated = s.save()
        self.assertEqual(updated.bio, 'I love Arabic!')