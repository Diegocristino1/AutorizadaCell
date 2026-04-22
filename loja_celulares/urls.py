from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Autorizada Cell — Administração'
admin.site.site_title = 'Autorizada Cell'
admin.site.index_title = 'Catálogo e mensagens'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
