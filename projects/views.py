from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.forms import ProjectForm
from projects.models import Project


def _page_context(request, queryset):
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return {"page_obj": page_obj, "projects": page_obj.object_list, "query_prefix": ""}


def project_list_view(request):
    queryset = Project.objects.select_related("owner").prefetch_related("participants")
    return render(request, "projects/project_list.html", _page_context(request, queryset))


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            if not project.participants.filter(pk=project.owner_id).exists():
                project.participants.add(project.owner)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def project_complete_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=403)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error"}, status=400)
    if project.participants.filter(pk=request.user.id).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project.id).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def favorite_projects_view(request):
    projects = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})
