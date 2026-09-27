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
]