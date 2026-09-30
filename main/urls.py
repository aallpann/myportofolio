from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_achievement,
    create_achievement,
    get_achievements_json,
    update_achievement,
    delete_achievement,
    create_experience,
    update_experience,
    delete_experience,
    register,
    login_user,
    logout_user,
    toggle_star,
    create_achievement_ajax,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievement/", show_achievement, name="show_achievement"),
    path("achievement/add/", create_achievement, name="create_achievement"),
    path("api/achievements/", get_achievements_json, name="get_achievements_json"),
    path("achievements/<int:achievement_id>/delete/",delete_achievement,name="delete_achievement"),
    path("achievement/<int:achievement_id>/edit/", update_achievement, name="update_achievement"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("achievements/<int:achievement_id>/star/", toggle_star, name="toggle_star"),
    path("achievement/add-ajax/", create_achievement_ajax, name="create_achievement_ajax"),
]