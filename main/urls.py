from django.urls import include, path
from rest_framework.routers import SimpleRouter

from main.views import (
    ContactMessageCreateView,
    ExperienceViewSet,
    ProfileView,
    ProjectViewSet,
    SkillCategoryViewSet,
    SocialLinkViewSet,
    api_root,
)

router = SimpleRouter(trailing_slash=True)
router.register('skills', SkillCategoryViewSet, basename='skills')
router.register('projects', ProjectViewSet, basename='projects')
router.register('experience', ExperienceViewSet, basename='experience')
router.register('socials', SocialLinkViewSet, basename='socials')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
    path('', include(router.urls)),
]
