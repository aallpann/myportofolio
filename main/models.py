import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, default="")
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None


class Achievement(models.Model):
    LEVEL_CHOICES = [
        ('school', 'Sekolah'),
        ('university', 'Universitas'),
        ('village', 'Desa'),
        ('district', 'Kecamatan'),
        ('city', 'Kota/Kabupaten'),
        ('province', 'Provinsi'),
        ('national', 'Nasional'),
        ('international', 'Internasional'),
    ]

    name = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    award = models.CharField(max_length=100)
    year = models.IntegerField()
    description = models.TextField()
    field = models.CharField(max_length=200)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)


class AchievementImage(models.Model):
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.achievement.name}"