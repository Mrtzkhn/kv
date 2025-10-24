from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from kvstore.models import KeyValue

User = get_user_model()


class KeyValueAPISmokeTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("keyvalue-list")
        self.detail = lambda key: reverse("keyvalue-detail", kwargs={"key": key})
        self.user = User.objects.create_user(username="alice", password="StrongPass123!")
        KeyValue.objects.create(key="site_title", value="My Site")

    def test_auth_required_for_list_and_retrieve(self):
        res = self.client.get(self.list_url)
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        res = self.client.get(self.detail("site_title"))
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_list_and_retrieve_with_auth(self):
        self.client.force_authenticate(user=self.user)

        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        keys = {item["key"] for item in res.data}
        self.assertIn("site_title", keys)

        res = self.client.get(self.detail("site_title"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["key"], "site_title")
        self.assertEqual(res.data["value"], "My Site")

    def test_put_updates_existing(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.put(self.detail("site_title"), {"value": "New Title"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["key"], "site_title")
        self.assertEqual(res.data["value"], "New Title")
        self.assertEqual(KeyValue.objects.get(key="site_title").value, "New Title")

    def test_put_creates_when_missing(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.put(self.detail("tagline"), {"value": "Just works"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["key"], "tagline")
        self.assertEqual(res.data["value"], "Just works")
        self.assertTrue(KeyValue.objects.filter(key="tagline", value="Just works").exists())

    def test_put_requires_value(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.put(self.detail("anything"), {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("value", res.data)

    def test_retrieve_missing_key_is_404(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.detail("does-not-exist"))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class KeyValueModelTests(APITestCase):
    def test_str_returns_key(self):
        obj = KeyValue.objects.create(key="foo", value="bar")
        self.assertEqual(str(obj), "foo")
