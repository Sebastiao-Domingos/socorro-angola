
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
]


urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('doacoes/', include('doacoes.urls')),
    path('incidentes/', include('incidentes.urls')),
    path('voluntarios/', include('voluntarios.urls')),
    prefix_default_language=False
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)