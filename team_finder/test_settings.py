from pathlib import Path

from team_finder.settings import *  # noqa: F403


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MEDIA_ROOT = BASE_DIR / ".test_media"
MEDIA_ROOT.mkdir(exist_ok=True)
