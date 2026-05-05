from django.urls import path

from users import views


app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.user_list_view, name="list"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("skills/", views.skill_autocomplete_view, name="skills"),
    path("skills/add/", views.add_user_skill_view, name="add_skill"),
    path("skills/<int:skill_id>/remove/", views.remove_user_skill_view, name="remove_skill"),
    path("<int:user_id>/", views.user_detail_view, name="detail"),
]
