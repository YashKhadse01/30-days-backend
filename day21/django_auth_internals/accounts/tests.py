
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase


class CustomUserTests(TestCase):
    def test_custom_user_model(self):
        User = get_user_model()
        self.assertEqual(User.__name__, "CustomUser")

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123!",
        )

        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("SecurePassword123!"))


class CustomPasswordHasherTests(TestCase):
    def test_custom_scrypt_algorithm(self):
        hashed = make_password("SecurePassword123!")
        self.assertTrue(hashed.startswith("custom_scrypt$"))

    def test_correct_password(self):
        hashed = make_password("SecurePassword123!")
        self.assertTrue(check_password("SecurePassword123!", hashed))

    def test_wrong_password(self):
        hashed = make_password("SecurePassword123!")
        self.assertFalse(check_password("WrongPassword", hashed))


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="backenduser",
            email="backend@example.com",
            password="SecurePassword123!",
        )

    def test_username_login(self):
        user = authenticate(
            username="backenduser",
            password="SecurePassword123!",
        )
        self.assertEqual(user, self.user)

    def test_email_login(self):
        user = authenticate(
            username="backend@example.com",
            password="SecurePassword123!",
        )
        self.assertEqual(user, self.user)

    def test_wrong_password(self):
        user = authenticate(
            username="backenduser",
            password="WrongPassword",
        )
        self.assertIsNone(user)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()

        user = authenticate(
            username="backenduser",
            password="SecurePassword123!",
        )
        self.assertIsNone(user)
