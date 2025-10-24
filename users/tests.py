from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


User = get_user_model()


class UsersAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")

    def test_register_success_creates_user_and_returns_201(self):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "StrongPass123!",
            "first_name": "Alice",
            "last_name": "Doe",
        }
        res = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(res.status_code, 201)
        # basic shape
        self.assertIn("username", res.data)
        self.assertIn("email", res.data)
        self.assertNotIn("password", res.data)  # write_only in serializer

        # user actually created & password hashed
        user = User.objects.get(username="alice")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_register_rejects_duplicate_email_case_insensitive(self):
        User.objects.create_user(
            username="existing", email="Dup@Example.com", password="StrongPass123!"
        )
        payload = {
            "username": "another",
            "email": "dup@example.com",  # different case
            "password": "AnotherStrong123!",
        }
        res = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)
        # serializer message
        self.assertTrue(
            any("already exists" in str(msg).lower() for msg in res.data["email"])
        )

    def test_register_short_password_is_rejected(self):
        payload = {"username": "bob", "email": "bob@example.com", "password": "short"}
        res = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("password", res.data)  # min length or validators error

    def test_register_missing_username(self):
        payload = {"email": "nouser@example.com", "password": "StrongPass123!"}
        res = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("username", res.data)

    def test_token_obtain_success(self):
        User.objects.create_user(
            username="charlie", email="charlie@example.com", password="StrongPass123!"
        )
        res = self.client.post(
            self.token_url,
            {"username": "charlie", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_token_obtain_invalid_credentials(self):
        User.objects.create_user(
            username="dana", email="dana@example.com", password="StrongPass123!"
        )
        res = self.client.post(
            self.token_url, {"username": "dana", "password": "wrongpass"}, format="json"
        )

        self.assertEqual(res.status_code, 401)
        self.assertNotIn("access", res.data)
        self.assertNotIn("refresh", res.data)

    def test_token_refresh_success(self):
        User.objects.create_user(
            username="ed", email="ed@example.com", password="StrongPass123!"
        )
        login = self.client.post(
            self.token_url, {"username": "ed", "password": "StrongPass123!"}, format="json"
        )
        self.assertEqual(login.status_code, 200)
        refresh_token = login.data["refresh"]

        res = self.client.post(self.refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
