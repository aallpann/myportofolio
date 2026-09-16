from django.shortcuts import render

from main.forms import AchievementForm
from main.models import Experience, Achievement

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


def show_main(request):
    context = {
        "name": "Alfan Kurnia Karim",
        "npm": "2506537814",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada dunia teknologi sekaligus bisnis."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Alfan Kurnia Karim",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_achievement(request):
    json_response = get_achievements_json(request)

    achievements = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    achievements = [achievement.object for achievement in achievements]
    name_query = request.GET.get("name", "").strip()

    context = {
        "name": "Alfan",
        "achievement_list": achievements,
        "name_query": name_query,
    }
    return render(request, "achievement.html", context)

def create_achievement(request):
    form = AchievementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Achievement baru berhasil ditambahkan!")
        return redirect("main:show_achievement")

    context = {
        "name": "Alfan",
        "form": form,
    }
    return render(request, "achievement_form.html", context)

def get_achievements_json(request):
    name_query = request.GET.get("title", "").strip()
    achievements = Achievement.objects.all()

    if name_query:
        achievements = Achievement.objects.filter(
            name__icontains=name_query
        )

    achievements_json = serializers.serialize("json", achievements)
    return HttpResponse(achievements_json, content_type="application/json")

def delete_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Achievement berhasil dihapus!")
        return redirect("main:show_achievement")

    return redirect("main:show_achievement")