from django.core.cache import cache
from django.db.models import Case, When, IntegerField

from src.discovery.services.video_discovery.search_video_resolution_service import SearchVideoResolutionService
from src.media.models import VideoItem, VideoCategoryPivot


class ListMediaService:
    def __init__(self) -> None:
        self.search_video_resolution_service = SearchVideoResolutionService()

    def _get_videos(self, qs, count, used_ids):
        """
        Helper:
        - excludes already used videos
        - returns limited queryset
        - updates used_ids set
        """
        videos = list(qs.exclude(id__in=used_ids)[:count])
        used_ids.update(v.id for v in videos)
        return videos

    def get_frontpage_queryset(self, tags: dict | None = None):
        video_ids = self._resolve_video_ids(tags)
        return self._build_queryset(video_ids)

    def _resolve_video_ids(self, tags: dict | None):
        if tags:
            video_ids = self.search_video_resolution_service.resolve_videos(tags)
            if video_ids:
                return video_ids

        return cache.get('frontpage_ids')

    def _build_queryset(self, video_ids):
        if video_ids:
            # preserve custom ranking order
            preserved_order = Case(
                *[
                    When(id=vid, then=pos)
                    for pos, vid in enumerate(video_ids)
                ],
                output_field=IntegerField(),
            )

            return VideoItem.objects.filter(
                id__in=video_ids
            ).order_by(preserved_order)

        # fallback default feed
        return VideoItem.objects.order_by('-id')

    def home_video_list(self, tags: dict | None = None, flatten: bool = False) -> dict:
        used_ids = set()
        base_qs = self.get_frontpage_queryset(tags)

        context = {
            "main_header": self._get_videos(
                base_qs, 6, used_ids
            ),

            "continue_watch": self._get_videos(
                base_qs, 13, used_ids
            ),

            "top_10_movies": self._get_videos(
                base_qs, 10, used_ids
            ),

            "only_on_site": self._get_videos(
                base_qs, 13, used_ids
            ),

            "fresh_picks": self._get_videos(
                base_qs, 12, used_ids
            ),

            "upcoming_movies": self._get_videos(
                base_qs, 15, used_ids
            ),

            "slider_videos": self._get_videos(
                base_qs, 15, used_ids
            ),

            "favourite_personality": self._get_videos(
                base_qs, 30, used_ids
            ),

            "popular_movies": self._get_videos(
                base_qs, 19, used_ids
            ),

            "big_middle_area": self._get_videos(
                base_qs, 5, used_ids
            ),

            "watch_now": self._get_videos(
                base_qs, 19, used_ids
            ),

            "recommended": self._get_videos(
                base_qs, 19, used_ids
            ),

            "top_picks": self._get_videos(
                base_qs, 19, used_ids
            ),
        }

        if flatten:
            context['video_list'] = self._flatten_home_videos(context)

        return context

    def _flatten_home_videos(self, videos: dict) -> list:
        video_list = []
        used_ids = set()

        for section_videos in videos.values():
            if not isinstance(section_videos, list):
                continue

            for video in section_videos:
                if video.id in used_ids:
                    continue

                video_list.append(video)
                used_ids.add(video.id)

        return video_list

    def single_video_list(self, video: VideoItem) -> dict:
        used_ids = set()
        category_ids = list(video.video_category_links.values_list("category_id", flat=True))
        video_ids = list(
            VideoCategoryPivot.objects
            .filter(category_id__in=category_ids)
            .exclude(video_id=video.id)
            .values_list('video_id', flat=True)
            .distinct()[:300]
        )
        base_qs = (
            VideoItem.objects.order_by("-id")
            .filter(slug_rewritten__isnull=False)
            .filter(id__in=list(video_ids))
        )

        context = {
            "recommended": self._get_videos(
                base_qs, 13, used_ids
            ),

            "more_to_watch": self._get_videos(
                base_qs, 20, used_ids
            ),

            "enjoy_this": self._get_videos(
                base_qs, 20, used_ids
            ),

            "new": self._get_videos(
                base_qs, 12, used_ids
            ),

            "upcoming_movies": self._get_videos(
                base_qs, 15, used_ids
            ),
        }

        return context
