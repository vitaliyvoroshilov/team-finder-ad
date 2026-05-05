from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import EmailValidator
from django.db import models
from django.urls import reverse

from users.constants import (
    ABOUT_MAX_LENGTH,
    AVATAR_UPLOAD_TO,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
)
from users.managers import UserManager
from users.services import build_avatar_content, build_avatar_filename
from core.validators import validate_github_url


class Skill(models.Model):
    name = models.CharField("Навык", max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "навык"
        verbose_name_plural = "навыки"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True, validators=[EmailValidator()])
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to=AVATAR_UPLOAD_TO, blank=True)
    phone = models.CharField("Телефон", max_length=PHONE_MAX_LENGTH, blank=True, null=True, unique=True)
    github_url = models.URLField(
        "Ссылка на GitHub",
        blank=True,
        validators=[validate_github_url],
    )
    about = models.TextField("О себе", max_length=ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )
    skills = models.ManyToManyField(Skill, related_name="users", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ("surname", "name", "email")
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"user_id": self.pk})

    def save(self, *args, **kwargs):
        if self.phone == "":
            self.phone = None
        if not self.avatar:
            self.avatar.save(
                build_avatar_filename(),
                ContentFile(build_avatar_content(self.name, self.email)),
                save=False,
            )
        super().save(*args, **kwargs)
