from src.media.models import VideoItem


class ListMediaService:
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

    def home_video_list(self) -> dict:
        used_ids = set()
        base_qs = VideoItem.objects.order_by("-id").all()

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

        return context

    def single_video_list(self) -> dict:
        used_ids = set()
        base_qs = VideoItem.objects.order_by("-id").all()

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
