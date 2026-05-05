from users.models import Skill, User


def get_users_queryset():
    return User.objects.prefetch_related("skills").order_by("surname", "name", "email")


def get_user_details_queryset():
    return get_users_queryset().prefetch_related("owned_projects__participants")


def get_skills_queryset(query=""):
    skills = Skill.objects.order_by("name")
    if query:
        skills = skills.filter(name__istartswith=query)
    return skills
