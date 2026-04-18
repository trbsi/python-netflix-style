from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.text import slugify

from src.media.models import VideoItem, VideoCategory, VideoCategoryPivot, VideoTranslation


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

    def get_videos_for_rewrite(self, limit: int, count: bool, latest: bool, category: bool) -> dict:
        if latest:
            videos: QuerySet[VideoItem] = VideoItem.objects.order_by("-id").filter(description__isnull=True)[:limit]
        elif category:
            last_category = cache.get('last_category_tmp')
            if not last_category:
                video_category = VideoCategory.objects.order_by('id').first()
            else:
                video_category = VideoCategory.objects.filter(id__gt=last_category).order_by('id').first()

            cache.set('last_category_tmp', video_category.id)
            video_ids = (VideoCategoryPivot.objects
                         .filter(category_id=video_category.id)
                         .values_list('video_id', flat=True)[:limit])

            videos: QuerySet[VideoItem] = VideoItem.objects.filter(id__in=list(video_ids))
        else:
            videos: QuerySet[VideoItem] = (
                VideoItem.objects
                .order_by("-id")
                .filter(slug_rewritten__isnull=True)[:limit]
            )

            # VideoItem.objects.filter(
            #     id__in=list(videos.values_list('id', flat=True)),
            #     slug_rewritten__isnull=True
            # ).update(slug_rewritten="__PROCESSING__")

        counter = VideoItem.objects.filter(slug_rewritten__isnull=False).count() if count else 0

        return {
            "info": {
                "count": counter
            },
            "items": [
                {
                    "video_id": v.id,
                    "title": v.title_rewritten if v.title_rewritten else v.title,
                }
                for v in videos
            ]
        }
