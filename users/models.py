import io
import random
import uuid
from urllib.parse import urlparse

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import EmailValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont


def validate_github_url(value):
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise ValidationError("Укажите корректную ссылку на GitHub.")


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean(exclude={"avatar"})
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("name", extra_fields.get("name", "Admin"))
        extra_fields.setdefault("surname", extra_fields.get("surname", "User"))
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField("Навык", max_length=124, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True, validators=[EmailValidator()])
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    phone = models.CharField("Телефон", max_length=12, blank=True, null=True, unique=True)
    github_url = models.URLField(
        "Ссылка на GitHub",
        blank=True,
        validators=[validate_github_url],
    )
    about = models.TextField("О себе", max_length=256, blank=True)
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
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def save(self, *args, **kwargs):
        if self.phone == "":
            self.phone = None
        if not self.avatar:
            self.avatar.save(
                self._avatar_filename(),
                ContentFile(self._build_avatar()),
                save=False,
            )
        super().save(*args, **kwargs)

    def _avatar_filename(self):
        return f"avatar_{uuid.uuid4()}.png"

    def _build_avatar(self):
        size = 256
        image = Image.new(
            "RGB",
            (size, size),
            color=random.choice(
                [
                    "#D9E6F2",
                    "#DDEBDB",
                    "#F1E2CC",
                    "#E7D9F2",
                    "#E9E2DA",
                    "#DCE8E6",
                ]
            ),
        )
        draw = ImageDraw.Draw(image)
        letter = (self.name[:1] or self.email[:1] or "?").upper()
        try:
            font = ImageFont.truetype("arial.ttf", 140)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), letter, font=font)
        x = (size - (bbox[2] - bbox[0])) / 2
        y = (size - (bbox[3] - bbox[1])) / 2 - 8
        draw.text((x, y), letter, fill="#1E293B", font=font)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
