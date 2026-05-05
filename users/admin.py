from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import Skill, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "surname", "skills_list", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about", "skills", "favorites")},
        ),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email", "name", "surname")

    @admin.display(description="Навыки")
    def skills_list(self, obj):
        return ", ".join(obj.skills.values_list("name", flat=True))


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)
