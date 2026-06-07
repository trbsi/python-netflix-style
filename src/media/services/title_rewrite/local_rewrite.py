from django.db.models import QuerySet
from django.utils.text import slugify

from automationapp import settings
from src.media.models import VideoItem, VideoTranslation, VideoCategory


class LocalRewriteService:

    def update_titles(self, payload: dict) -> list:
        slug_rewritten_field = VideoItem._meta.get_field('slug_rewritten')
        slug_translation = VideoTranslation._meta.get_field('slug')

        items = payload if isinstance(payload, list) else payload.get('items', [])

        updated = []

        for item in items:
            video_id = item.get('video_id')
            title = item.get('title')
            description = item.get('description')
            lang = item.get('lang')

            if not video_id:
                continue

            try:
                video: VideoItem = VideoItem.objects.get(pk=video_id)
            except VideoItem.DoesNotExist:
                continue

            if lang is not None and lang != 'en':
                if lang == 'hr':
                    VideoTranslation.objects.create(
                        video=video,
                        language_code='sr',
                        title=title,
                        slug=slugify(title)[:slug_translation.max_length],
                        description=description,
                    )
                VideoTranslation.objects.create(
                    video=video,
                    language_code=lang,
                    title=title,
                    slug=slugify(title)[:slug_translation.max_length],
                    description=description,
                )
            else:
                if title:
                    video.title_rewritten = title
                    video.slug_rewritten = slugify(title)[:slug_rewritten_field.max_length]
                if description:
                    video.description = description
                video.save()

            updated.append(video_id)

        return updated

    def get_videos_for_rewrite(self, limit: int, count: bool, lang: str, last_id: int) -> dict:
        if lang == 'en':
            category_ids = VideoCategory.objects.filter(
                slug__in=settings.FIXED_CATEGORIES
            ).values_list("id", flat=True)

            videos = (
                VideoItem.objects
                .filter(
                    video_category_links__category_id__in=list(category_ids),
                    slug_rewritten__isnull=True,
                )
                .order_by('video_category_links__video_id')
                .distinct()
                [:limit]
            )

        else:
            videos: QuerySet[VideoItem] = (
                VideoItem.objects
                .order_by("id")
                .filter(id__gt=last_id)[:limit]
            )

        counter = VideoItem.objects.filter(slug_rewritten__isnull=False).count() if count else 0
        videos_list = list(videos.values_list("id", flat=True))

        return {
            "info": {
                "count": counter
            },
            "last_id": videos_list[-1] if videos_list else 999_999_999,
            "items": [
                {
                    "video_id": v.id,
                    "title": v.title_rewritten if v.title_rewritten else v.title,
                    "tags": v.tags,
                }
                for v in videos
            ]
        }
