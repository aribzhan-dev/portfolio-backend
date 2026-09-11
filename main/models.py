from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

LEVEL_MIN = 0
LEVEL_MAX = 100


class TimeStampedOrderedModel(models.Model):
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ['order']


class Profile(models.Model):
    full_name = models.CharField('Имя и фамилия', max_length=100)
    role = models.CharField('Должность', max_length=150)
    bio = models.TextField('О себе')
    photo = models.ImageField('Фото', upload_to='profile/', blank=True)
    email = models.EmailField('Email')
    location = models.CharField('Локация', max_length=100, blank=True)
    cv_file = models.FileField('Файл резюме', upload_to='cv/', blank=True)
    cv_url = models.URLField('Ссылка на резюме', blank=True)
    years_experience = models.PositiveIntegerField('Лет опыта', default=0)
    projects_count = models.PositiveIntegerField('Количество проектов', default=0)
    is_available = models.BooleanField('Открыт к предложениям', default=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профиль'

    def __str__(self):
        return self.full_name


class SkillCategory(TimeStampedOrderedModel):
    name = models.CharField('Название', max_length=100)
    icon = models.CharField('Иконка (эмодзи)', max_length=10, blank=True)

    class Meta(TimeStampedOrderedModel.Meta):
        verbose_name = 'Категория навыков'
        verbose_name_plural = 'Категории навыков'

    def __str__(self):
        return self.name


class Skill(TimeStampedOrderedModel):
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name='Категория',
    )
    name = models.CharField('Название', max_length=100)
    level = models.PositiveIntegerField(
        'Уровень, %',
        validators=[MinValueValidator(LEVEL_MIN), MaxValueValidator(LEVEL_MAX)],
    )

    class Meta(TimeStampedOrderedModel.Meta):
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return f'{self.name} ({self.level}%)'


class Tag(models.Model):
    """Loyiha kartochkasida ko'rsatiladigan texnologiya yorlig'i.

    `Skill` dan alohida, chunki loyihada ishlatilgan har bir texnologiya
    ko'nikmalar ro'yxatida foiz bilan turishi shart emas
    (masalan "Spring Boot", "AI/LLM").
    """

    name = models.CharField('Название', max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Project(TimeStampedOrderedModel):
    class ProjectType(models.TextChoices):
        WEB = 'web', 'Веб-приложение'
        MOBILE = 'mobile', 'Мобильное приложение'
        API = 'api', 'API-сервис'
        BOT = 'bot', 'Бот'

    title = models.CharField('Название', max_length=100)
    slug = models.SlugField('Слаг (URL)', max_length=100, unique=True)
    short_description = models.CharField('Краткое описание', max_length=200, blank=True)
    description = models.TextField('Полное описание')
    image = models.ImageField('Обложка', upload_to='projects/', blank=True)
    project_type = models.CharField(
        'Тип проекта',
        max_length=10,
        choices=ProjectType.choices,
        default=ProjectType.WEB,
        db_index=True,
    )
    tags = models.ManyToManyField(Tag, verbose_name='Технологии', blank=True)
    github_url = models.URLField('Ссылка на GitHub', blank=True)
    live_url = models.URLField('Ссылка на демо', blank=True)
    is_featured = models.BooleanField('Показать в избранном', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta(TimeStampedOrderedModel.Meta):
        ordering = ['order', '-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.title


class Experience(TimeStampedOrderedModel):
    class Kind(models.TextChoices):
        WORK = 'work', 'Работа'
        EDUCATION = 'education', 'Образование'

    title = models.CharField('Должность / специальность', max_length=100)
    organization = models.CharField('Организация', max_length=100)
    description = models.TextField('Описание', blank=True)
    kind = models.CharField('Тип', max_length=10, choices=Kind.choices, default=Kind.WORK)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta(TimeStampedOrderedModel.Meta):
        ordering = ['order', '-start_date']
        verbose_name = 'Опыт'
        verbose_name_plural = 'Опыт и образование'

    def __str__(self):
        return f'{self.title} — {self.organization}'

    @property
    def is_current(self):
        return self.end_date is None


class SocialLink(TimeStampedOrderedModel):
    class Icon(models.TextChoices):
        GITHUB = 'github', 'GitHub'
        LINKEDIN = 'linkedin', 'LinkedIn'
        TELEGRAM = 'telegram', 'Telegram'
        EMAIL = 'email', 'Email'

    name = models.CharField('Название', max_length=100)
    url = models.URLField('Ссылка')
    icon = models.CharField('Иконка', max_length=20, choices=Icon.choices)

    class Meta(TimeStampedOrderedModel.Meta):
        verbose_name = 'Соцсеть'
        verbose_name_plural = 'Соцсети'

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Получено', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.name} <{self.email}>'
