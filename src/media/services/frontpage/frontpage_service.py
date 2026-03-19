import random
from datetime import timedelta

import bugsnag
from django.core.cache import cache
from django.utils import timezone

from src.media.models import VideoItem


class FrontpageService:
    def generate_frontpage(self) -> int:
        week = timezone.now() - timedelta(days=7)
        total_videos = 200

        # 1. Try getting all videos from last week
        candidates = list(
            VideoItem.objects.filter(external_created_at__gte=week)
            .values_list('id', flat=True)
        )

        # 2. If there aren’t enough, take additional videos from older entries
        if len(candidates) < total_videos:
            # Get the remaining number needed
            remaining = total_videos - len(candidates)

            # Exclude the already included IDs
            extra_candidates = list(
                VideoItem.objects.exclude(id__in=candidates)
                .order_by('-id')
                .values_list('id', flat=True)[:remaining]
            )

            candidates.extend(extra_candidates)

        # 3. Shuffle and take exactly total_videos
        if len(candidates) < total_videos:
            e = ValueError(f"Not enough videos to generate frontpage. Found {len(candidates)}")
            bugsnag.notify(e)
            raise e

        selected_ids = random.sample(candidates, total_videos)

        # 4. Cache and return
        cache.set('frontpage_ids', selected_ids, 60 * 60 * 24)
        cache.delete('frontpage_html')
        
        return len(selected_ids)
