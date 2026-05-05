from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            name="Olga",
            surname="Sidorova",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="testpass123",
            name="Petr",
            surname="Smirnov",
        )

    def test_create_project_adds_owner_to_participants(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "Team Finder",
                "description": "Backend implementation",
                "github_url": "https://github.com/example/team-finder",
                "status": Project.STATUS_OPEN,
            },
        )
        project = Project.objects.get(name="Team Finder")
        self.assertRedirects(response, reverse("projects:detail", args=[project.id]))
        self.assertEqual(project.owner, self.owner)
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_toggle_participate(self):
        project = Project.objects.create(
            name="API",
            description="Test project",
            owner=self.owner,
            github_url="https://github.com/example/api",
        )
        project.participants.add(self.owner)
        self.client.force_login(self.member)

        response = self.client.post(reverse("projects:toggle_participate", args=[project.id]))
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertTrue(project.participants.filter(pk=self.member.pk).exists())

    def test_complete_project(self):
        project = Project.objects.create(
            name="Web",
            description="Test project",
            owner=self.owner,
            github_url="https://github.com/example/web",
        )
        project.participants.add(self.owner)
        self.client.force_login(self.owner)

        response = self.client.post(reverse("projects:complete", args=[project.id]))
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.STATUS_CLOSED)
