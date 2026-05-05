import io
import random
import re
import uuid

from PIL import Image, ImageDraw, ImageFont

from users.constants import (
    AVATAR_BACKGROUND_COLORS,
    AVATAR_DEFAULT_LETTER,
    AVATAR_FILENAME_PREFIX,
    AVATAR_FONT_NAME,
    AVATAR_FONT_SIZE,
    AVATAR_IMAGE_FORMAT,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_Y_OFFSET,
    PHONE_PATTERN,
)


PHONE_RE = re.compile(PHONE_PATTERN)


def normalize_phone(phone):
    if not phone:
        return None
    phone = phone.strip()
    if phone.startswith("8"):
        return f"+7{phone[1:]}"
    return phone


def build_avatar_filename():
    return f"{AVATAR_FILENAME_PREFIX}_{uuid.uuid4()}.png"


def build_avatar_content(name, email):
    image = Image.new(
        "RGB",
        (AVATAR_SIZE, AVATAR_SIZE),
        color=random.choice(AVATAR_BACKGROUND_COLORS),
    )
    draw = ImageDraw.Draw(image)
    letter = (name[:1] or email[:1] or AVATAR_DEFAULT_LETTER).upper()
    try:
        font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (bbox[2] - bbox[0])) / 2
    y = (AVATAR_SIZE - (bbox[3] - bbox[1])) / 2 + AVATAR_TEXT_Y_OFFSET
    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)
    buffer = io.BytesIO()
    image.save(buffer, format=AVATAR_IMAGE_FORMAT)
    return buffer.getvalue()


def get_users_queryset():
    from users.models import User

    return User.objects.prefetch_related("skills").order_by("surname", "name", "email")


def get_user_details_queryset():
    return get_users_queryset().prefetch_related("owned_projects__participants")


def get_skills_queryset(query=""):
    from users.models import Skill

    skills = Skill.objects.order_by("name")
    if query:
        skills = skills.filter(name__istartswith=query)
    return skills
