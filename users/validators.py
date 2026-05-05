from urllib.parse import urlparse

from django.core.exceptions import ValidationError

from users.constants import GITHUB_HOSTS


def validate_github_url(value):
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in GITHUB_HOSTS:
        raise ValidationError("Укажите корректную ссылку на GitHub.")
