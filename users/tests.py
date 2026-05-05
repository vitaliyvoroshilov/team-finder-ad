import json

from django.test import Client, TestCase
from django.urls import reverse

from users.models import Skill, User


class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            name="Ivan",
            surname="Petrov",
        )

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
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ivan Petrov")
        self.assertEqual(response.context["active_skill"], "Python")

    def test_add_and_remove_user_skill(self):
        self.client.force_login(self.user)
        add_response = self.client.post(
            reverse("users:add_skill", args=[self.user.id]),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(add_response.status_code, 200)
        skill = Skill.objects.get(name="Django")
        self.assertTrue(self.user.skills.filter(pk=skill.pk).exists())

        remove_response = self.client.post(
            reverse("users:remove_skill", args=[self.user.id, skill.id]),
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(self.user.skills.filter(pk=skill.pk).exists())
