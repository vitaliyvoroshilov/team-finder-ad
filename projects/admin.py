from django.contrib import admin

from projects.models import Project
from projects.services import get_projects_queryset


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "participants_count", "created_at")
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("name", "owner__email", "owner__name", "owner__surname")
    autocomplete_fields = ("owner", "participants")

    def get_queryset(self, request):
        return get_projects_queryset()

    @admin.display(description="Количество участников", ordering="participants_count")
    def participants_count(self, obj):
        return obj.participants_count
