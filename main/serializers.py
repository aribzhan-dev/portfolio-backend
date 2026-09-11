from rest_framework import serializers

from main.models import (
    ContactMessage,
    Experience,
    Profile,
    Project,
    Skill,
    SkillCategory,
    SocialLink,
)

MESSAGE_MIN_LENGTH = 10
MESSAGE_MAX_LENGTH = 1000


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'level']


class SkillCategorySerializer(serializers.ModelSerializer):
    """Kategoriya va uning ichidagi ko'nikmalar — bitta so'rovda."""

    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'icon', 'skills']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'full_name',
            'role',
            'bio',
            'photo',
            'email',
            'location',
            'cv_file',
            'cv_url',
            'years_experience',
            'projects_count',
            'is_available',
        ]


class ProjectSerializer(serializers.ModelSerializer):
    # Frontend `tags` ni oddiy matnlar ro'yxati sifatida kutadi
    tags = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'slug',
            'short_description',
            'description',
            'image',
            'project_type',
            'tags',
            'github_url',
            'live_url',
            'is_featured',
        ]


class ExperienceSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = Experience
        fields = [
            'id',
            'title',
            'organization',
            'description',
            'kind',
            'start_date',
            'end_date',
            'is_current',
        ]


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['id', 'name', 'url', 'icon']


class ContactMessageSerializer(serializers.ModelSerializer):
    """Tashqi ma'lumot — shuning uchun har bir maydon alohida tekshiriladi."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError('Укажите ваше имя.')
        return name

    def validate_message(self, value):
        message = value.strip()
        if len(message) < MESSAGE_MIN_LENGTH:
            raise serializers.ValidationError(
                f'Сообщение слишком короткое — минимум {MESSAGE_MIN_LENGTH} символов.'
            )
        if len(message) > MESSAGE_MAX_LENGTH:
            raise serializers.ValidationError(
                f'Сообщение не должно быть длиннее {MESSAGE_MAX_LENGTH} символов.'
            )
        return message
