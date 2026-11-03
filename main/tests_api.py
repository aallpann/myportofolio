from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Achievement


class AchievementAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
            email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor",
            password="test-password",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="test-password",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(self.editor_group)

        self.achievement = Achievement.objects.create(
            name="Portfolio Achievement",
            organizer="University",
            award="Winner",
            year=2026,
            description="A test achievement",
            field="Business Case",
            level="university",
        )

        self.list_url = reverse("api:achievement-list")
        self.detail_url = reverse(
            "api:achievement-detail", args=[self.achievement.id]
        )
        self.star_url = reverse(
            "api:achievement-star", args=[self.achievement.id]
        )
        self.payload = {
            "name": "New Achievement",
            "organizer": "University",
            "award": "First Winner",
            "year": 2026,
            "description": "A useful achievement",
            "field": "Technology",
            "level": "national",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.achievement.id)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])

        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["name"], self.achievement.name)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"name": "PORTFOLIO"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {"name": "not-found"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_achievement(self):
        url = reverse("api:achievement-detail", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)

            create_response = self.client.post(
                self.list_url, self.payload, format="json"
            )
            self.assertEqual(
                create_response.status_code, status.HTTP_403_FORBIDDEN
            )

            update_response = self.client.patch(
                self.detail_url, {"name": "Changed"}, format="json"
            )
            self.assertEqual(
                update_response.status_code, status.HTTP_403_FORBIDDEN
            )

            delete_response = self.client.delete(self.detail_url)
            self.assertEqual(
                delete_response.status_code, status.HTTP_403_FORBIDDEN
            )

        self.assertEqual(Achievement.objects.count(), 1)
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.name, "Portfolio Achievement")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url, self.payload, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertTrue(
            Achievement.objects.filter(pk=response.data["id"]).exists()
        )

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)

        for changes, field in [
            ({"name": "   "}, "name"),
            ({"name": '<img src="x" onerror="alert(1)">'} , "name"),
        ]:
            response = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )
            self.assertIn(field, response.data)

        self.assertEqual(Achievement.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url, {"name": "Changed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.description, "A test achievement")

        response = self.client.put(
            self.detail_url, {"name": "Incomplete"}, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

        response = self.client.put(
            self.detail_url, self.payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(response.content, b"")
        self.assertFalse(
            Achievement.objects.filter(pk=self.achievement.id).exists()
        )

    def test_star_requires_login_and_toggles(self):
        response = self.client.post(self.star_url)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
            },
            format="json",
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        update_response = self.client.patch(
            self.detail_url, {"name": "Editor Updated"}, format="json"
        )
        self.assertEqual(
            update_response.status_code, status.HTTP_200_OK
        )

        create_response = self.client.post(
            self.list_url, self.payload, format="json"
        )
        self.assertEqual(
            create_response.status_code, status.HTTP_403_FORBIDDEN
        )

        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(
            delete_response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.list_url)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )

        response = client.post(
            self.list_url, self.payload, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(Achievement.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )

        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )