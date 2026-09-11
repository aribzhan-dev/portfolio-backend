from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from main.models import ContactMessage, Experience, Project, Skill, SkillCategory

pytestmark = pytest.mark.unit


def test_profile_str_returns_full_name(profile):
    # Arrange / Act
    result = str(profile)

    # Assert
    assert result == 'Арибжан Камилжанов'


def test_skill_str_includes_level(skill_category):
    # Arrange
    skill = skill_category.skills.get(name='Python')

    # Act
    result = str(skill)

    # Assert
    assert result == 'Python (90%)'


def test_skill_level_above_100_is_rejected(db, skill_category):
    # Arrange
    skill = Skill(category=skill_category, name='Магия', level=150)

    # Act / Assert
    with pytest.raises(ValidationError):
        skill.full_clean()


def test_skill_level_below_zero_is_rejected(db, skill_category):
    # Arrange
    skill = Skill(category=skill_category, name='Ничего', level=-1)

    # Act / Assert
    with pytest.raises(ValidationError):
        skill.full_clean()


def test_experience_without_end_date_is_current(current_job):
    # Act / Assert
    assert current_job.is_current is True


def test_experience_with_end_date_is_not_current(db):
    # Arrange
    finished = Experience.objects.create(
        title='Backend-разработчик',
        organization='Компания',
        kind=Experience.Kind.WORK,
        start_date=date(2022, 3, 1),
        end_date=date(2023, 5, 1),
    )

    # Act / Assert
    assert finished.is_current is False


def test_project_slug_must_be_unique(db, web_project):
    # Arrange / Act / Assert
    with pytest.raises(IntegrityError):
        Project.objects.create(
            title='Другой проект',
            slug=web_project.slug,
            description='Описание.',
        )


def test_categories_are_ordered_by_order_field(db):
    # Arrange
    SkillCategory.objects.create(name='Второй', order=2)
    SkillCategory.objects.create(name='Первый', order=1)

    # Act
    names = list(SkillCategory.objects.values_list('name', flat=True))

    # Assert
    assert names == ['Первый', 'Второй']


def test_contact_messages_are_ordered_newest_first(db):
    # Arrange
    ContactMessage.objects.create(name='Первый', email='a@example.com', message='Раз.')
    ContactMessage.objects.create(name='Второй', email='b@example.com', message='Два.')

    # Act
    names = list(ContactMessage.objects.values_list('name', flat=True))

    # Assert
    assert names == ['Второй', 'Первый']


def test_project_defaults_to_web_type(db):
    # Arrange / Act
    project = Project.objects.create(title='Сайт', slug='site', description='Описание.')

    # Assert
    assert project.project_type == Project.ProjectType.WEB
