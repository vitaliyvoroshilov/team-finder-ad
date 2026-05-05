from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.forms import ProjectForm
from projects.models import Project
from projects.services import get_projects_queryset
from team_finder.services import build_page_context


def project_list_view(request):
    return render(request, "projects/project_list.html", build_page_context(request, get_projects_queryset()))


def project_detail_view(request, project_id):
    project = get_object_or_404(get_projects_queryset(), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create_view(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save()
        if not project.participants.filter(pk=project.owner_id).exists():
            project.participants.add(project.owner)
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def project_complete_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)
    if is_participant := project.participants.filter(pk=request.user.id).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not is_participant})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if is_favorited := request.user.favorites.filter(pk=project.id).exists():
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not is_favorited})


@login_required
def favorite_projects_view(request):
    projects = get_projects_queryset().filter(interested_users=request.user)
    return render(request, "projects/favorite_projects.html", {"projects": projects})
