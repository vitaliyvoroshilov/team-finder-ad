import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from users.models import User, validate_github_url


PHONE_RE = re.compile(r"^(8\d{10}|\+7\d{10})$")


def normalize_phone(phone):
    if not phone:
        return None
    phone = phone.strip()
    if phone.startswith("8"):
        return f"+7{phone[1:]}"
    return phone


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Введите email"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "about": forms.Textarea(attrs={"rows": 4, "placeholder": "Расскажите о себе"}),
            "phone": forms.TextInput(attrs={"placeholder": "+79991234567"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/username"}),
            "avatar": forms.FileInput(attrs={"accept": "image/*", "hidden": True}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return None
        phone = phone.strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
        phone = normalize_phone(phone)
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Такой номер телефона уже используется.")
        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        validate_github_url(github_url)
        return github_url


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Текущий пароль", widget=forms.PasswordInput())
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput())
    new_password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput())
