from django.core.cache import cache

from automationapp import settings
from src.media.models import VideoCategory, VideoCategoryPivot


def limited_video_ids():
    video_ids = cache.get('fixed_video_ids_v2')
    if video_ids:
        return video_ids

    category_ids = VideoCategory.objects.filter(slug__in=settings.FIXED_CATEGORIES).values_list('id', flat=True)
    video_ids = []
    for category_id in category_ids:
        video_ids += (
            VideoCategoryPivot.objects
            .filter(category_id=category_id)
            .order_by('id')
            .values_list('video_id', flat=True)[:settings.FIXED_HARD_LIMIT_PER_CATEGORY]
        )

    cache.set('fixed_video_ids_v2', video_ids, 60 * 60)
    return video_ids
