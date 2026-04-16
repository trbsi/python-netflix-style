from django.shortcuts import get_object_or_404

from src.core.utils import GRADUAL_ROLLOUT
from src.media.models import VideoItem, VideoCategory, VideoCategoryPivot


class SearchByCategoryService:
    PAGE_SIZE = 25

    def search_videos_api(self, slug: str, last_id: int) -> tuple:
        category = get_object_or_404(VideoCategory, slug=slug)

        query = VideoCategoryPivot.objects.filter(category=category).order_by('-video_id')
        if last_id > 0:
            query = query.filter(video_id__lt=last_id)

        video_ids = query.values_list('video_id', flat=True)[:self.PAGE_SIZE + 1]
        has_next = len(video_ids) > self.PAGE_SIZE

        video_ids = video_ids[:self.PAGE_SIZE]
        videos = VideoItem.objects.filter(pk__in=video_ids).order_by('id')

        result = []

        for video in videos:
            result.append({
                "id": video.id,
                "title": video.main_title,
                "thumbnail": video.thumbnail_small,
                "duration": video.duration_formatted,
                "url": video.video_url,
                "categories": [
                    {
                        "title": c['title'],
                        "slug": c['slug']
                    } for c in video.categories_array
                ]
            })

        return result, has_next

    def get_category_videos_with_gradual_rollout(self, slug, last_id=0):
        category = get_object_or_404(VideoCategory, slug=slug)

        # 1. Base query limited to MAX_VIDEOS
        base_ids = (
            VideoCategoryPivot.objects
            .filter(category=category)
            .order_by('-video_id')
            .values_list('video_id', flat=True)[:GRADUAL_ROLLOUT]
        )

        # 2. Apply cursor inside that limited set
        query = VideoCategoryPivot.objects.filter(
            category=category,
            video_id__in=list(base_ids)
        )

        if last_id and last_id > 0:
            query = query.filter(video_id__lt=last_id)

        # 3. Pagination slice
        video_ids = list(
            query.order_by('-video_id')
            .values_list('video_id', flat=True)[:self.PAGE_SIZE + 1]
        )

        has_next = len(video_ids) > self.PAGE_SIZE
        video_ids = video_ids[:self.PAGE_SIZE]

        # 4. Fetch objects
        videos = list(
            VideoItem.objects.filter(id__in=video_ids)
        )

        videos.sort(key=lambda x: x.id, reverse=True)

        next_last_id = videos[-1].id if videos else None

        return {
            "results": videos,
            "has_next": has_next,
            "next_last_id": next_last_id,
        }

    def get_category_videos(self, slug, last_id=0):
        """
        Cursor-based pagination for category videos.
        Fast, scalable, no JOIN/DISTINCT issues.
        """

        # 1. Get category
        category = get_object_or_404(VideoCategory, slug=slug)

        # 2. Base pivot query (only pivot table)
        query = VideoCategoryPivot.objects.filter(category=category)

        # 3. Apply cursor (keyset pagination)
        if last_id and last_id > 0:
            query = query.filter(video_id__lt=last_id)

        # 4. Fetch one extra item to detect next page
        video_ids = list(
            query.order_by('-video_id')
            .values_list('video_id', flat=True)[:self.PAGE_SIZE + 1]
        )

        # 5. Determine if next page exists
        has_next = len(video_ids) > self.PAGE_SIZE

        # 6. Keep only current page
        video_ids = video_ids[:self.PAGE_SIZE]

        # 7. Fetch real objects
        videos = list(
            VideoItem.objects.filter(id__in=video_ids)
        )

        # 8. Preserve ordering (important because IN() is unordered)
        videos.sort(key=lambda x: x.id, reverse=True)

        # 9. Next cursor (IMPORTANT for frontend)
        next_last_id = videos[-1].id if videos else None

        # 10. Return clean cursor response (NO paginator, NO Page)
        return {
            "results": videos,
            "has_next": has_next,
            "next_last_id": next_last_id,
        }
