from django.contrib import admin
from django.urls import path, include, register_converter
from django.urls.converters import StringConverter
from django.conf import settings
from django.conf.urls.static import static


class PersianSlugConverter(StringConverter):
    regex = r"[-\w\u0600-\u06FF]+"


register_converter(PersianSlugConverter, 'persian_slug')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('accommodations/', include(('accommodations.urls', 'accommodations'), namespace='accommodations')),
    path('estate/', include(('estate.urls', 'estate'), namespace='estate')),
    path('marketplace/', include(('marketplace.urls', 'marketplace'), namespace='marketplace')),
    path('magazine/', include(('magazine.urls', 'magazine'), namespace='magazine')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('ckeditor5/', include('django_ckeditor_5.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
