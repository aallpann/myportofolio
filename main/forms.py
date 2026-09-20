from django.forms import ModelForm, TextInput, Textarea, URLInput, inlineformset_factory

from main.models import Achievement, AchievementImage

class AchievementForm(ModelForm):
    class Meta:
        model = Achievement
        fields =[
            "name",
            "organizer",
            "award",
            "year",
            "description",
            "field",
            "level",
        ]

        labels = {
            "name": "Nama Perlombaan",
            "organizer": "Nama Penyelenggara",
            "award": "Jenis Penghargaan",
            "year": "Tahun Penghargaan Diraih",
            "description": "Deskripsi Penghargaan",
            "field": "Cabang Lomba dari Penghargaan",
            "level": "Tingkat atau Level Penghargaan",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Nama Perlombaan",
                    "maxlength": 255,
                }
            ),
            "organizer": TextInput(
                attrs={
                    "placeholder": "Nama Penyelenggara",
                    "maxlength": 255,
                }
            ),
            "award": TextInput(
                attrs={
                    "placeholder": "Jenis Penghargaan",
                    "maxlength": 100,
                }
            ),
            "year": TextInput(
                attrs={
                    "placeholder": "Tahun Penghargaan (Cth: 2026)",
                    "maxlength": 12,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Deskripsi Penghargaan",
                    "row": 3,
                }
            ),
            "field": TextInput(
                attrs={
                    "placeholder": "Cabang Penghargaan",
                    "maxlength": 255,
                }
            ),
            "level": TextInput(
                attrs={
                    "placeholder": "Tingkat Penghargaan",
                    "maxlength": 255,
                }
            ),
        }

class AchievementImageForm(ModelForm):
    class Meta:
        model = AchievementImage
        fields = ["image_url"]

        widgets = {
            "image_url": TextInput(
                attrs={
                    "placeholder": "URL gambar achievement"
                }
            ),
        }

AchievementImageFormSet = inlineformset_factory(
    Achievement,
    AchievementImage,
    form=AchievementImageForm,
    extra=3,
    can_delete=True,
)