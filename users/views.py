from http import HTTPStatus

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.services import build_page_context, load_json_body
from users.forms import LoginForm, ProfileEditForm, RegistrationForm, UserPasswordChangeForm
from users.models import Skill
from users.services import get_skills_queryset, get_user_details_queryset, get_users_queryset


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request, request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(get_user_details_queryset(), pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


def user_list_view(request):
    active_skill = request.GET.get("skill")
    users = get_users_queryset()
    if active_skill:
        users = users.filter(skills__name=active_skill).distinct()
    all_skills = list(get_skills_queryset().values_list("name", flat=True))
    context = build_page_context(
        request,
        users,
        base_context={
            "participants": users,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )
    return render(request, "users/participants.html", context)


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_autocomplete_view(request):
    query = request.GET.get("q", "").strip()
    return JsonResponse(list(get_skills_queryset(query).values("id", "name")[:10]), safe=False)


@login_required
@require_POST
def add_user_skill_view(request):
    data = load_json_body(request)
    skill_id = data.get("skill_id")
    name = (data.get("name") or "").strip()
    created = False
    if skill_id:
        skill = get_object_or_404(get_skills_queryset(), pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "error", "message": "Нет данных навыка"}, status=HTTPStatus.BAD_REQUEST)
    if added := not request.user.skills.filter(pk=skill.pk).exists():
        request.user.skills.add(skill)
    return JsonResponse(
        {
            "status": "ok",
            "id": skill.id,
            "name": skill.name,
            "skill_id": skill.id,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_user_skill_view(request, skill_id):
    skill = get_object_or_404(get_skills_queryset(), pk=skill_id)
    if not request.user.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {"status": "error", "message": "Навык не найден у пользователя"},
            status=HTTPStatus.NOT_FOUND,
        )
    request.user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
