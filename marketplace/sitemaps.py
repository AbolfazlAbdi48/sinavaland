from django.contrib.sitemaps import Sitemap
from .models import Product


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(
            is_available=True,
            stock__gt=0
        )

    def lastmod(self, obj):
        return obj.updated_at
