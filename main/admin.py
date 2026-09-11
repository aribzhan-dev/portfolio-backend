from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from main.models import (
    ContactMessage,
    Experience,
    Profile,
    Project,
    Skill,
    SkillCategory,
    SocialLink,
    Tag,
)

# Saytda auth yo'q — "Группы" bo'limi keraksiz, panelni chalkashtiradi
admin.site.unregister(Group)

admin.site.site_header = 'Портфолио'
admin.site.site_title = 'Портфолио'
admin.site.index_title = 'Управление содержимым сайта'

THUMBNAIL_SIZE_PX = 45


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profil bitta bo'ladi: qo'shish va o'chirish tugmalari yashiriladi."""

    list_display = ['full_name', 'role', 'email', 'is_available']
    fieldsets = [
        ('Основное', {'fields': ['full_name', 'role', 'bio', 'photo']}),
        ('Контакты', {'fields': ['email', 'location', 'is_available']}),
        ('Резюме', {'fields': ['cv_file', 'cv_url']}),
        ('Статистика на сайте', {'fields': ['years_experience', 'projects_count']}),
    ]

    def has_add_permission(self, request):
        return not Profile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class SkillInline(admin.TabularInline):
    """Ko'nikmalar o'z kategoriyasi ichida tahrirlanadi."""

    model = Skill
    extra = 1
    fields = ['name', 'level', 'order']


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'skill_count', 'order']
    list_editable = ['order']
    inlines = [SkillInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('skills')

    @admin.display(description='Навыков')
    def skill_count(self, obj):
        return obj.skills.count()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['preview', 'title', 'project_type', 'is_featured', 'order']
    list_display_links = ['preview', 'title']
    list_editable = ['is_featured', 'order']
    list_filter = ['project_type', 'is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ['title']}
    filter_horizontal = ['tags']
    readonly_fields = ['created_at']

    @admin.display(description='Обложка')
    def preview(self, obj):
        if not obj.image:
            return '—'
        return format_html(
            '<img src="{}" style="height:{}px;border-radius:6px;object-fit:cover;" />',
            obj.image.url,
            THUMBNAIL_SIZE_PX,
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'kind', 'start_date', 'end_date', 'order']
    list_editable = ['order']
    list_filter = ['kind']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'url', 'order']
    list_editable = ['order']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Xabarlar faqat sayt orqali keladi — admin'da tahrirlanmaydi."""

    list_display = ['name', 'email', 'short_message', 'is_read', 'created_at']
    list_editable = ['is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'message', 'created_at']

    def has_add_permission(self, request):
        return False

    @admin.display(description='Сообщение')
    def short_message(self, obj):
        limit = 60
        if len(obj.message) <= limit:
            return obj.message
        return f'{obj.message[:limit]}…'
