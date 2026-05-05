from django import forms

from projects.models import Project
from team_finder.mixins import GithubUrlCleanMixin


class ProjectForm(GithubUrlCleanMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Введите название проекта"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "Расскажите о проекте"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/org/repo"}),
            "status": forms.Select(),
        }
