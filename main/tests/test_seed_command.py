import pytest
from django.core.management import call_command

from main.models import Profile, Project, Skill, SkillCategory, SocialLink, Tag

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_seed_creates_all_content():
    # Act
    call_command('seed_portfolio', verbosity=0)

    # Assert
    assert Profile.objects.count() == 1
    assert SkillCategory.objects.count() == 4
    assert Skill.objects.count() == 19
    assert Project.objects.count() == 6
    assert SocialLink.objects.count() == 2
    assert Tag.objects.exists()


def test_seed_is_idempotent():
    # Arrange
    call_command('seed_portfolio', verbosity=0)

    # Act — ikkinchi marta ishga tushiramiz
    call_command('seed_portfolio', verbosity=0)

    # Assert — dublikat yaratilmadi
    assert Profile.objects.count() == 1
    assert Skill.objects.count() == 19
    assert Project.objects.count() == 6


def test_seed_links_tags_to_projects():
    # Act
    call_command('seed_portfolio', verbosity=0)

    # Assert
    project = Project.objects.get(slug='rent-car')
    assert sorted(project.tags.values_list('name', flat=True)) == [
        'Java',
        'JavaScript',
        'PostgreSQL',
        'React',
        'Spring Boot',
    ]


def test_reset_flag_clears_old_content():
    # Arrange
    call_command('seed_portfolio', verbosity=0)
    Project.objects.create(title='Старый', slug='old-one', description='Удалить.')

    # Act
    call_command('seed_portfolio', '--reset', verbosity=0)

    # Assert
    assert not Project.objects.filter(slug='old-one').exists()
    assert Project.objects.count() == 6
