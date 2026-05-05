import json
from urllib.parse import urlencode

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from users.forms import LoginForm, ProfileEditForm, RegistrationForm, UserPasswordChangeForm
from users.models import Skill, User


def _page_context(request, queryset, *, base_context=None):
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    query_prefix = f"{urlencode(params)}&" if params else ""
    context = {"page_obj": page_obj, "query_prefix": query_prefix}
    if base_context:
        context.update(base_context)
    return context


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("projects:list")
    else:
        form = LoginForm(request)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects__participants"),
        pk=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


def user_list_view(request):
    active_skill = request.GET.get("skill")
    users = User.objects.prefetch_related("skills").order_by("id")
    if active_skill:
        users = users.filter(skills__name=active_skill).distinct()
    all_skills = list(Skill.objects.order_by("name").values_list("name", flat=True))
    context = _page_context(
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
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_autocomplete_view(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.order_by("name")
    if query:
        skills = skills.filter(name__istartswith=query)
    return JsonResponse(list(skills.values("id", "name")[:10]), safe=False)


def _load_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


@login_required
@require_POST
def add_user_skill_view(request, user_id):
    if request.user.id != user_id:
        return HttpResponseForbidden()
    profile_user = get_object_or_404(User, pk=user_id)
    data = _load_json_body(request)
    skill_id = data.get("skill_id")
    name = (data.get("name") or "").strip()
    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "error", "message": "Нет данных навыка"}, status=400)
    added = not profile_user.skills.filter(pk=skill.pk).exists()
    if added:
        profile_user.skills.add(skill)
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
def remove_user_skill_view(request, user_id, skill_id):
    if request.user.id != user_id:
        return HttpResponseForbidden()
    profile_user = get_object_or_404(User, pk=user_id)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not profile_user.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error", "message": "Навык не найден у пользователя"}, status=404)
    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
