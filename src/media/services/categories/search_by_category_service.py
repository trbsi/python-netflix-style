from django.core.paginator import Paginator, Page
from django.shortcuts import get_object_or_404

from automationapp import settings
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

    def get_category_videos(self, slug: str, last_id: int = 0):
        category = get_object_or_404(VideoCategory, slug=slug)

        HARD_LIMIT = settings.FIXED_HARD_LIMIT_PER_CATEGORY
        PAGE_SIZE = self.PAGE_SIZE

        base_query = VideoCategoryPivot.objects.filter(category=category).order_by("video_id")

        # Step 1: freeze the universe to HARD_LIMIT items
        limited_ids = list(
            base_query.values_list("video_id", flat=True)[:HARD_LIMIT]
        )

        # Step 2: apply cursor inside that frozen set
        if last_id:
            limited_ids = [vid for vid in limited_ids if vid > last_id]

        # Step 3: paginate
        page_ids = limited_ids[:PAGE_SIZE]

        videos = list(VideoItem.objects.filter(id__in=page_ids).filter(slug_rewritten__isnull=False))
        videos.sort(key=lambda x: x.id, reverse=True)

        next_last_id = videos[-1].id if videos else None
        has_next = len(limited_ids) > PAGE_SIZE

        return {
            "results": videos,
            "has_next": has_next,
            "next_last_id": next_last_id,
        }

    def get_category_videos_WITHOUT_HARD_LIMIT(self, slug, last_id=0):
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
            query = query.filter(video_id__gt=last_id)

        # 4. Fetch one extra item to detect next page
        video_ids = list(
            query.order_by('video_id')
            .values_list('video_id', flat=True)[:self.PAGE_SIZE + 1]
        )

        # 5. Determine if next page exists
        has_next = len(video_ids) > self.PAGE_SIZE

        # 6. Keep only current page
        video_ids = video_ids[:self.PAGE_SIZE]

        # 7. Fetch real objects
        videos = list(
            VideoItem.objects.filter(id__in=video_ids).filter(slug_rewritten__isnull=False)
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

    def get_category_videos_paginator(self, slug, page=1) -> Page:
        category = get_object_or_404(VideoCategory, slug=slug)
        videos = (
            VideoItem.objects
            .filter(video_category_links__category_id=category.id)
            .filter(slug_rewritten__isnull=False)
            .order_by('-id')[:settings.FIXED_HARD_LIMIT_PER_CATEGORY]
        )
        paginator = Paginator(object_list=videos, per_page=self.PAGE_SIZE)
        return paginator.page(page)
