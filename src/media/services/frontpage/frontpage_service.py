import random
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from src.media.models import VideoItem


class FrontpageService:
    def generate_frontpage(self) -> int:
        week = timezone.now() - timedelta(days=7)
        max_id = VideoItem.objects.order_by('-id').first().id
        min_id = VideoItem.objects.order_by('id').filter(external_created_at=week).id

        ids = set()
        total_videos = 200  # sum of src.media.services.home.list_media_service.ListMediaService.home_video_list

        while len(ids) < total_videos:
            rand = random.randint(min_id, max_id)
            if VideoItem.objects.filter(id=rand).exists():
                ids.add(rand)

        cache.set('frontpage_ids', list(ids), 60 * 60 * 24)

        return len(ids)
