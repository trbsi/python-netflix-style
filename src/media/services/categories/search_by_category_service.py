from django.core.paginator import Paginator
from django.urls import reverse_lazy

from src.media.models import VideoItem


class SearchByCategoryService:
    def search_videos(self, slug: str, page: int) -> tuple:
        videos_qs = (
            VideoItem.objects
            .filter(categories_relation__slug=slug)
            .prefetch_related('categories_relation')
            .order_by("-id")
            .distinct()
        )

        paginator = Paginator(videos_qs, 20)
        page_obj = paginator.get_page(page)

        videos = []

        for video in page_obj:
            videos.append({
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail_small,
                "duration": video.duration_formatted,
                "url": reverse_lazy("media.single_video", kwargs={"id": video.id}, ),
                "categories": [
                    {
                        "title": c['title'],
                        "slug": c['slug']
                    } for c in video.categories_array
                ]
            })

        return videos, page_obj.has_next()
