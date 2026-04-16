from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from src.media.models import VideoItem, VideoCategory, VideoCategoryPivot


class SearchByCategoryService:
    PAGE_SIZE = 20

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

    def search_videos(self, slug: str, page_number: int = 1):
        category = get_object_or_404(VideoCategory, slug=slug)

        queryset = (
            VideoItem.objects
            .filter(categories=category)
            .order_by('-id')
            .distinct()
        )

        paginator = Paginator(queryset, self.PAGE_SIZE)
        page = paginator.get_page(page_number)

        return page
