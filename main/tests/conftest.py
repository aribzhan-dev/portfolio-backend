from datetime import date

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from main.models import (
    Experience,
    Profile,
    Project,
    Skill,
    SkillCategory,
    SocialLink,
    Tag,
)


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Har bir test toza rate-limit hisobi bilan boshlanadi."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def profile(db):
    return Profile.objects.create(
        full_name='Арибжан Камилжанов',
        role='Full-stack разработчик',
        bio='Разрабатываю веб-приложения полного цикла.',
        email='test@example.com',
        location='Астана, Казахстан',
        years_experience=3,
        projects_count=12,
    )


@pytest.fixture
def skill_category(db):
    category = SkillCategory.objects.create(name='Backend', icon='⚙️', order=0)
    Skill.objects.create(category=category, name='Python', level=90, order=0)
    Skill.objects.create(category=category, name='Django', level=88, order=1)
    return category


@pytest.fixture
def web_project(db):
    project = Project.objects.create(
        title='Платформа обучения',
        slug='learning-platform',
        short_description='LMS с курсами.',
        description='Полноценная система управления обучением.',
        project_type=Project.ProjectType.WEB,
        is_featured=True,
        order=0,
    )
    project.tags.set(
        [Tag.objects.create(name=name) for name in ('Django', 'Python')]
    )
    return project


@pytest.fixture
def bot_project(db):
    return Project.objects.create(
        title='Telegram-бот',
        slug='analytics-bot',
        description='Бот для отчётов.',
        project_type=Project.ProjectType.BOT,
        is_featured=False,
        order=1,
    )


@pytest.fixture
def current_job(db):
    return Experience.objects.create(
        title='Full-stack разработчик',
        organization='Фриланс',
        description='Разработка под ключ.',
        kind=Experience.Kind.WORK,
        start_date=date(2023, 6, 1),
        end_date=None,
        order=0,
    )


@pytest.fixture
def social_link(db):
    return SocialLink.objects.create(
        name='GitHub',
        url='https://github.com/example',
        icon=SocialLink.Icon.GITHUB,
        order=0,
    )
