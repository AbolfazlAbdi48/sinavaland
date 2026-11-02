from django.contrib.sitemaps import Sitemap
from .models import Estate


class EstateSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Estate.objects.filter(is_available=True)

    def lastmod(self, obj):
        return obj.updated_at
