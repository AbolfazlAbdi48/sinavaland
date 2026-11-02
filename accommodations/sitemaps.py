from django.contrib.sitemaps import Sitemap
from .models import Accommodation


class AccommodationSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Accommodation.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
