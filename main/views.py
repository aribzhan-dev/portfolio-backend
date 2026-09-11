import logging

from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from main.models import Experience, Profile, Project, SkillCategory, SocialLink
from main.serializers import (
    ContactMessageSerializer,
    ExperienceSerializer,
    ProfileSerializer,
    ProjectSerializer,
    SkillCategorySerializer,
    SocialLinkSerializer,
)

logger = logging.getLogger(__name__)

TRUE_VALUES = {'true', '1', 'yes'}


class ProfileView(RetrieveAPIView):
    """GET /api/profile/ — bitta profil. Ro'yxat emas, obyekt qaytaradi."""

    serializer_class = ProfileSerializer

    def get_object(self):
        profile = Profile.objects.first()
        if profile is None:
            logger.warning('Profile obyekti bazada yo\'q — admin orqali qo\'shilmagan.')
            raise Http404('Профиль ещё не заполнен.')
        return profile


class SkillCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/skills/ — kategoriyalar, ichida ko'nikmalar bilan."""

    serializer_class = SkillCategorySerializer
    # prefetch_related — N+1 so'rovning oldini oladi
    queryset = SkillCategory.objects.prefetch_related('skills')


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/projects/ va /api/projects/<slug>/

    Filtrlar: ?type=web&featured=true
    """

    serializer_class = ProjectSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Project.objects.prefetch_related('tags')

        project_type = self.request.query_params.get('type')
        if project_type:
            queryset = queryset.filter(project_type=project_type)

        featured = self.request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(is_featured=featured.lower() in TRUE_VALUES)

        return queryset


class ExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/experience/ — ish tajribasi va ta'lim."""

    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()


class SocialLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/socials/ — ijtimoiy tarmoq havolalari."""

    serializer_class = SocialLinkSerializer
    queryset = SocialLink.objects.all()


class ContactMessageCreateView(CreateAPIView):
    """POST /api/contact/ — bog'lanish formasi.

    Auth yo'q, shuning uchun spamdan himoya sifatida rate limit qo'yilgan.
    """

    serializer_class = ContactMessageSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.info('Bog\'lanish formasi validatsiyadan o\'tmadi: %s', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info('Yangi xabar qabul qilindi: %s', serializer.validated_data['email'])

        return Response(
            {'detail': 'Сообщение отправлено. Спасибо!'},
            status=status.HTTP_201_CREATED,
        )


@api_view(['GET'])
def api_root(request):
    """GET /api/ — mavjud endpointlar ro'yxati.

    Ildiz (`/`) shu yerga yo'naltiriladi, chunki sayt frontend'i alohida
    serverda ishlaydi — Django faqat API va admin panelni beradi.
    """
    return Response(
        {
            'profile': request.build_absolute_uri('/api/profile/'),
            'skills': request.build_absolute_uri('/api/skills/'),
            'projects': request.build_absolute_uri('/api/projects/'),
            'experience': request.build_absolute_uri('/api/experience/'),
            'socials': request.build_absolute_uri('/api/socials/'),
            'contact': request.build_absolute_uri('/api/contact/'),
            'admin': request.build_absolute_uri('/admin/'),
        }
    )
