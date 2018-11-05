from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view
from markdownx import urls as markdownx

schema_view = get_swagger_view(title='Qandor API')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', obtain_jwt_token),
    url(r'^markdownx/', include(markdownx)),
    url(r'^$', schema_view),
    url(r'^api/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
