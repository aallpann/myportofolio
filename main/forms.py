from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from django.forms import ModelForm, TextInput, Textarea, URLInput, DateInput, Select, inlineformset_factory

from main.models import Achievement, AchievementImage, Experience

class AchievementForm(ModelForm):

    def clean_name(self):
        name = strip_tags(self.cleaned_data["name"]).strip()
        if not name:
            raise ValidationError(
                "Nama achievement tidak boleh hanya berisi tag HTML."
            )
        return name

    def clean_organizer(self):
        return strip_tags(self.cleaned_data["organizer"]).strip()

    def clean_award(self):
        return strip_tags(self.cleaned_data["award"]).strip()

    def clean_field(self):
        return strip_tags(self.cleaned_data["field"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

    class Meta:
        model = Achievement

        fields = [
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
            "level": Select(),
        }

class AchievementImageForm(ModelForm):
    class Meta:
        model = AchievementImage
        fields = ["image_url"]

        widgets = {
            "image_url": URLInput(
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

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience

        fields = [
            "title",
            "organization",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Nama Pengalaman",
            "organization": "Nama Organisasi",
            "description": "Deskripsi Pengalaman",
            "category": "Kategori Pengalaman",
            "thumbnail": "URL Gambar",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Nama Kegiatan",
                }
            ),

            "organization": TextInput(
                attrs={
                    "placeholder": "Penyelenggara Kegiatan",
                }
            ),

            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalaman kamu",
                    "rows": 4,
                }
            ),

            "category": Select(),

            "thumbnail": URLInput(
                attrs={
                    "placeholder": "URL Gambar Pengalaman",
                }
            ),

            "started_at": DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),

            "ended_at": DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
        }