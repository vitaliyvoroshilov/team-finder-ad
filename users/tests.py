import json
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users.models import Skill, User


class UserViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            name="Ivan",
            surname="Petrov",
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_register_view_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Anna",
                "surname": "Ivanova",
                "email": "anna@example.com",
                "password": "strongpass123",
            },
        )
        self.assertRedirects(response, reverse("projects:list"))
        created_user = User.objects.get(email="anna@example.com")
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(str(created_user.id), self.client.session["_auth_user_id"])

    def test_users_list_filters_by_skill(self):
        skill = Skill.objects.create(name="Python")
        self.user.skills.add(skill)
        response = self.client.get(reverse("users:list"), {"skill": "Python"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Ivan Petrov")
        self.assertEqual(response.context["active_skill"], "Python")

    def test_add_and_remove_user_skill(self):
        add_response = self.user_client.post(
            reverse("users:add_skill"),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(add_response.status_code, HTTPStatus.OK)
        skill = Skill.objects.get(name="Django")
        self.assertTrue(self.user.skills.filter(pk=skill.pk).exists())

        remove_response = self.user_client.post(reverse("users:remove_skill", args=[skill.id]))
        self.assertEqual(remove_response.status_code, HTTPStatus.OK)
        self.assertFalse(self.user.skills.filter(pk=skill.pk).exists())
