from django.shortcuts import render

from main.models import Experience, Achievement


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
    achievement_list = Achievement.objects.all()

    context = {
        'achievement_list': achievement_list,
    }
    return render(request, 'achievement.html', context)