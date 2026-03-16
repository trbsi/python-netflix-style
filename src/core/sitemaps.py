# sitemaps.py

from django.contrib.sitemaps import Sitemap

from src.media.models import VideoItem, VideoCategory


class VideoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return VideoItem.objects.order_by('id')

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return VideoCategory.objects.order_by('id')
