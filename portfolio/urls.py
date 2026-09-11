from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Sayt frontend'i alohida serverda (:5173). Django faqat API va admin beradi,
    # shuning uchun ildizni API ro'yxatiga yo'naltiramiz.
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),
]

# Rasm va fayllar faqat development'da Django orqali beriladi.
# Productionda buni nginx yoki S3 qiladi.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
