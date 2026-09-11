"""Portfolio ma'lumotlarini bazaga yozadi.

Ishlatish:
    python manage.py seed_portfolio          # bo'sh bazani to'ldiradi
    python manage.py seed_portfolio --reset  # avval eski kontentni o'chiradi

Bu buyruq idempotent: qayta ishga tushirilsa dublikat yaratmaydi.
Xabarlar (ContactMessage) va foydalanuvchilarga tegmaydi.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from main.models import Profile, Project, Skill, SkillCategory, SocialLink, Tag

PROFILE = {
    'full_name': 'Арибжан Камилжанов',
    'role': 'Full-Stack разработчик',
    'bio': (
        'Я занимаюсь программированием уже 1.5–2 года. За это время реализовал '
        'множество реальных проектов как самостоятельно, так и в команде, включая '
        'веб-сайты и мобильные приложения. Backend: Python (Django, FastAPI, DRF), '
        'есть опыт с Java и C#, который сейчас углублённо изучаю. Базы данных: '
        'PostgreSQL, MySQL, SQLite, MongoDB, Redis. Frontend: HTML, CSS, JavaScript, '
        'React, сейчас пишу проекты на TypeScript. Также имею опыт работы с WebSocket '
        'для real-time приложений.'
    ),
    'email': 'aribzankamilzanov@gmail.com',
    'location': 'Астана, Казахстан',
    'years_experience': 2,
    'projects_count': 6,
    'is_available': True,
}

# (kategoriya nomi, ikonka, tartib, [(ko'nikma, daraja, tartib), ...])
SKILL_CATEGORIES = [
    ('Языки', '💻', 1, [
        ('Python', 90, 1),
        ('JavaScript', 80, 2),
        ('TypeScript', 70, 3),
        ('C#', 55, 4),
        ('Java', 55, 5),
        ('HTML', 90, 6),
        ('CSS', 85, 7),
    ]),
    ('Backend', '⚙️', 2, [
        ('FastAPI', 88, 1),
        ('Django', 88, 2),
        ('DRF', 85, 3),
        ('WebSocket', 75, 4),
        ('REST API', 88, 5),
    ]),
    ('Frontend', '🎨', 3, [
        ('React', 78, 1),
        ('Tailwind CSS', 82, 2),
    ]),
    ('Базы данных', '🗄️', 4, [
        ('PostgreSQL', 82, 1),
        ('MySQL', 70, 2),
        ('SQLite', 85, 3),
        ('MongoDB', 60, 4),
        ('Redis', 65, 5),
    ]),
]

GITHUB_URL = 'https://github.com/aribzhan-dev'

# CV fayli `media/` ichida saqlanadi va git'ga qo'shilmaydi.
# Agar server'da shu yo'lda fayl bo'lsa, profilga avtomatik biriktiriladi.
CV_RELATIVE_PATH = 'cv/Aribzhan_Kamilzhanov_CV.pdf'

PROJECTS = [
    {
        'title': 'Система автоматизации аренды авто (Rent Car)',
        'slug': 'rent-car',
        'short_description': 'Онлайн-бронирование машин, договоры и отчёты автоматически.',
        'description': (
            'Полностью автоматизированная система для аренды автомобилей. Клиенты могут '
            'бронировать машины онлайн, платежи, договоры и отчёты управляются автоматически.'
        ),
        'project_type': Project.ProjectType.WEB,
        'tags': ['Java', 'Spring Boot', 'React', 'JavaScript', 'PostgreSQL'],
        'github_url': GITHUB_URL,
        'live_url': '',
        'is_featured': True,
        'order': 1,
    },
    {
        'title': 'Safa — приложение для благотворительности и туров',
        'slug': 'safa',
        'short_description': 'Мобильное приложение: пожертвования и туры. Я делал backend API.',
        'description': (
            'Мобильное приложение, объединяющее услуги благотворительности и туризма. '
            'Пользователи могут делать пожертвования и получать информацию о турах. '
            'Я разработал backend API.'
        ),
        'project_type': Project.ProjectType.MOBILE,
        'tags': ['Python', 'FastAPI', 'PostgreSQL', 'REST API'],
        'github_url': GITHUB_URL,
        'live_url': '',
        'is_featured': True,
        'order': 2,
    },
    {
        'title': 'Do-It-Ly — менеджер командных задач',
        'slug': 'do-it-ly',
        'short_description': 'Назначение задач, отслеживание прогресса и автоотчёты.',
        'description': (
            'Платформа для управления командными задачами. Руководители назначают задачи '
            'сотрудникам, отслеживается прогресс, и автоматически формируются отчёты.'
        ),
        'project_type': Project.ProjectType.WEB,
        'tags': ['Python', 'Django', 'DRF', 'React', 'PostgreSQL', 'Redis'],
        'github_url': GITHUB_URL,
        'live_url': '',
        'is_featured': True,
        'order': 3,
    },
    {
        'title': 'Telegram-бот для учебных центров (AI)',
        'slug': 'education-bot',
        'short_description': 'Расписание, оценки и задания в Telegram, с интеграцией ИИ.',
        'description': (
            'Telegram-бот для автоматизации учебных центров. Ученики и преподаватели могут '
            'видеть расписание, оценки и задания. Интеграция с ИИ — опыт работы в AI Engineering.'
        ),
        'project_type': Project.ProjectType.BOT,
        'tags': ['Python', 'Telegram Bot API', 'AI/LLM', 'PostgreSQL', 'Redis'],
        'github_url': GITHUB_URL,
        'live_url': '',
        'is_featured': True,
        'order': 4,
    },
    {
        'title': 'Shukir.kz — сайт благотворительного фонда',
        'slug': 'shukir-kz',
        'short_description': 'Сайт крупного фонда в Казахстане: админ-панель и сбор пожертвований.',
        'description': (
            'Полнофункциональный веб-сайт, разработанный для крупного благотворительного фонда '
            'в Казахстане. Интерактивная админ-панель, сбор пожертвований и отчёты.'
        ),
        'project_type': Project.ProjectType.WEB,
        'tags': ['Python', 'Django', 'PostgreSQL', 'HTML', 'CSS'],
        'github_url': GITHUB_URL,
        'live_url': 'https://shukir.kz',
        'is_featured': True,
        'order': 5,
    },
    {
        'title': 'Real-Time Chat Bot',
        'slug': 'realtime-chat-bot',
        'short_description': 'Чат на WebSocket: несколько собеседников, история сообщений.',
        'description': (
            'Real-time чат-бот, созданный на основе технологии WebSocket. Одновременное общение '
            'с несколькими пользователями, история сообщений и управление активными подключениями.'
        ),
        'project_type': Project.ProjectType.BOT,
        'tags': ['Python', 'FastAPI', 'WebSocket', 'React', 'JavaScript'],
        'github_url': GITHUB_URL,
        'live_url': '',
        'is_featured': False,
        'order': 6,
    },
]

SOCIAL_LINKS = [
    ('GitHub', GITHUB_URL, SocialLink.Icon.GITHUB, 1),
    ('Email', f'mailto:{PROFILE["email"]}', SocialLink.Icon.EMAIL, 2),
]


class Command(BaseCommand):
    help = 'Portfolio kontentini bazaga yozadi (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Avval mavjud kontentni o\'chiradi (xabarlarga tegmaydi).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        self._seed_profile()
        self._seed_skills()
        self._seed_projects()
        self._seed_socials()

        self.stdout.write(self.style.SUCCESS('Ma\'lumotlar yozildi.'))

    def _reset(self):
        Project.objects.all().delete()
        Tag.objects.all().delete()
        SkillCategory.objects.all().delete()
        SocialLink.objects.all().delete()
        Profile.objects.all().delete()
        self.stdout.write('Eski kontent o\'chirildi.')

    def _seed_profile(self):
        profile = Profile.objects.first()
        if profile is None:
            profile = Profile.objects.create(**PROFILE)
            self.stdout.write('Profil yaratildi.')
        else:
            for field, value in PROFILE.items():
                setattr(profile, field, value)
            profile.save()
            self.stdout.write('Profil yangilandi.')

        self._attach_cv(profile)

    def _attach_cv(self, profile):
        """CV fayli media/ ichida mavjud bo'lsa — profilga biriktiradi."""
        cv_path = settings.MEDIA_ROOT / CV_RELATIVE_PATH

        if not cv_path.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'CV topilmadi: {cv_path}. Admin panel orqali yuklang.'
                )
            )
            return

        if profile.cv_file.name != CV_RELATIVE_PATH:
            profile.cv_file = CV_RELATIVE_PATH
            profile.save(update_fields=['cv_file'])
        self.stdout.write('CV biriktirildi.')

    def _seed_skills(self):
        for name, icon, order, skills in SKILL_CATEGORIES:
            category, _ = SkillCategory.objects.update_or_create(
                name=name,
                defaults={'icon': icon, 'order': order},
            )
            for skill_name, level, skill_order in skills:
                Skill.objects.update_or_create(
                    category=category,
                    name=skill_name,
                    defaults={'level': level, 'order': skill_order},
                )
        self.stdout.write(f'Ko\'nikmalar: {Skill.objects.count()} ta.')

    def _seed_projects(self):
        for data in PROJECTS:
            tag_names = data.pop('tags')
            slug = data.pop('slug') or slugify(data['title'])

            project, _ = Project.objects.update_or_create(slug=slug, defaults=data)
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            project.tags.set(tags)

            data['tags'] = tag_names
            data['slug'] = slug

        self.stdout.write(f'Loyihalar: {Project.objects.count()} ta.')

    def _seed_socials(self):
        for name, url, icon, order in SOCIAL_LINKS:
            SocialLink.objects.update_or_create(
                name=name,
                defaults={'url': url, 'icon': icon, 'order': order},
            )
        self.stdout.write(f'Havolalar: {SocialLink.objects.count()} ta.')
