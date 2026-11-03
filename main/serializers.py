
from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Achievement, AchievementImage


class AchievementSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Achievement
        fields = [
            "id", "name", "organizer", "award",
            "year", "description", "field", "level",
            "star_count", "is_starred", "starred_by_names",
            "images", "uploaded_images",
        ]
        read_only_fields = ["id", "images"]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_organizer(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())

    def get_images(self, obj):
        request = self.context.get("request")
        result = []

        for achievement_image in obj.images.all():
            if achievement_image.image:
                image_url = achievement_image.image.url
                if request is not None:
                    image_url = request.build_absolute_uri(image_url)
                result.append(image_url)
            elif achievement_image.image_url:
                result.append(achievement_image.image_url)

        return result

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        achievement = Achievement.objects.create(**validated_data)

        for uploaded_image in uploaded_images:
            AchievementImage.objects.create(
                achievement=achievement,
                image=uploaded_image,
            )

        return achievement

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()

        for uploaded_image in uploaded_images:
            AchievementImage.objects.create(
                achievement=instance,
                image=uploaded_image,
            )

        return instance
