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
        """Cursor-based pagination for category videos, capped at settings.FIXED_HARD_LIMIT_PER_CATEGORY total results."""
        category = get_object_or_404(VideoCategory, slug=slug)
        base_query = VideoCategoryPivot.objects.filter(category=category)

        already_served = base_query.filter(video_id__gt=last_id).count() if last_id else 0
        remaining = settings.FIXED_HARD_LIMIT_PER_CATEGORY - already_served
        if remaining <= 0:
            return {"results": [], "has_next": False, "next_last_id": None}

        fetch_size = min(self.PAGE_SIZE, remaining)
        query = base_query.filter(video_id__lt=last_id) if last_id else base_query
        video_ids = list(
            query.order_by('-video_id')
            .values_list('video_id', flat=True)[:fetch_size + 1]
        )

        has_next = len(video_ids) > fetch_size and already_served + fetch_size < settings.FIXED_HARD_LIMIT_PER_CATEGORY
        video_ids = video_ids[:fetch_size]

        videos = list(VideoItem.objects.filter(id__in=video_ids))
        videos.sort(key=lambda x: x.id, reverse=True)
        next_last_id = videos[-1].id if videos else None

        return {"results": videos, "has_next": has_next, "next_last_id": next_last_id}

    def get_category_videos_paginator(self, slug, page=1) -> Page:
        category = get_object_or_404(VideoCategory, slug=slug)
        videos = VideoItem.objects.filter(video_category_links__category_id=category.id).order_by('-id')
        paginator = Paginator(object_list=videos, per_page=self.PAGE_SIZE)
        return paginator.page(page)
