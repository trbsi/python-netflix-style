from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from src.media.models import VideoCategory


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return VideoCategory.objects.order_by('id')


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ['chat.about', 'media.categories', 'media.all_videos']

    def location(self, item):
        return reverse(item)
