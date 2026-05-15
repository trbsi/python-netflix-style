from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from src.media.models import VideoCategory, VideoItem
from src.media.utils.utils import limited_video_ids


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return VideoCategory.objects.order_by('id')


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ['media.categories', 'media.all_videos']

    def location(self, item):
        return reverse(item)


class VideosSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return VideoItem.objects.filter(id__in=limited_video_ids()).order_by('id')
