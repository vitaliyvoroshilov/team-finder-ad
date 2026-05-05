from django.db.models import Count

from projects.models import Project


def get_projects_queryset():
    return (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .annotate(participants_count=Count("participants", distinct=True))
        .order_by(*Project._meta.ordering)
    )
