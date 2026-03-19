from django.contrib.sitemaps import Sitemap

from src.media.models import VideoCategory


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return VideoCategory.objects.order_by('id')
