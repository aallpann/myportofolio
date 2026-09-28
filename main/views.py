import datetime

from django.shortcuts import redirect, render

from main.forms import AchievementForm, AchievementImageFormSet, ExperienceForm
from main.models import Experience, Achievement

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied 

def is_editor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name="Editor").exists()
    )


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Alfan Kurnia Karim",
        "npm": "2506537814",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada dunia teknologi sekaligus bisnis."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Alfan",
        "experience_list": Experience.objects.all(),
        "is_editor": is_editor(request.user),
    }

    return render(request, "experience.html", context)

def show_achievement(request):
    json_response = get_achievements_json(request)

    achievements = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    achievements = [achievement.object for achievement in achievements]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Alfan",
        "achievement_list": achievements,
        "title_query": title_query,
        "is_editor": is_editor(request.user),
    }
    return render(request, "achievement.html", context)

@login_required(login_url="/login/")
def create_achievement(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = AchievementForm(request.POST or None)
    image_formset = AchievementImageFormSet(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and image_formset.is_valid():
            achievement = form.save()

            image_formset.instance = achievement
            image_formset.save()

            messages.success(
                request,
                "Achievement baru berhasil ditambahkan!"
            )
            return redirect("main:show_achievement")

    context = {
        "name": "Alfan",
        "form": form,
        "image_formset": image_formset,
    }

    return render(request, "achievement_form.html", context)

def get_achievements_json(request):
    title_query = request.GET.get("title", "").strip()
    achievements = Achievement.objects.all()

    if title_query:
        achievements = Achievement.objects.filter(
            name__icontains=title_query
        )

    achievements_json = serializers.serialize(
        "json",
        achievements,
        use_natural_foreign_keys=True
    )

    return HttpResponse(
        achievements_json,
        content_type="application/json"
    )

@login_required(login_url="/login/")
def delete_achievement(request, achievement_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    achievement = get_object_or_404(
        Achievement,
        pk=achievement_id
    )

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Achievement berhasil dihapus!")
        return redirect("main:show_achievement")

    return redirect("main:show_achievement")

@login_required(login_url="/login/")
def update_achievement(request, achievement_id):
    if not (
        request.user.is_superuser
        or is_editor(request.user)
    ):
        raise PermissionDenied
    
    achievement = get_object_or_404(
        Achievement,
        pk=achievement_id
    )

    form = AchievementForm(
        request.POST or None,
        instance=achievement
    )

    image_formset = AchievementImageFormSet(
        request.POST or None,
        instance=achievement
    )

    if request.method == "POST":
        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()

            messages.success(
                request,
                "Achievement berhasil diperbarui!"
            )
            return redirect("main:show_achievement")

    context = {
        "name": "Alfan",
        "form": form,
        "image_formset": image_formset,
        "achievement": achievement,
    }

    return render(
        request,
        "achievement_edit.html",
        context
    )

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Alfan",
        "form": form,
    }

    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not (
        request.user.is_superuser
        or is_editor(request.user)
    ):
        raise PermissionDenied

    experience = get_object_or_404(
        Experience,
        pk=experience_id
    )

    form = ExperienceForm(
        request.POST or None,
        instance=experience
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Experience berhasil diperbarui!"
        )
        return redirect("main:show_experience")

    context = {
        "name": "Alfan",
        "form": form,
        "experience": experience,
    }

    return render(
        request,
        "experience_edit.html",
        context
    )

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(
        Experience,
        pk=experience_id
    )

    if request.method == "POST":
        experience.delete()
        messages.success(
            request,
            "Experience berhasil dihapus!"
        )
        return redirect("main:show_experience")

    return redirect("main:show_experience")     

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Alfan",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Alfan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star(request, achievement_id):
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in achievement.starred_by.all():
            achievement.starred_by.remove(request.user)
        else:
            achievement.starred_by.add(request.user)

    return redirect("main:show_achievement")