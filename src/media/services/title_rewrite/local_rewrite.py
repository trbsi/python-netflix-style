from django.utils.text import slugify

from src.media.models import VideoItem


class LocalRewriteService:

    def update_titles(self, payload: dict) -> list:
        field = VideoItem._meta.get_field('slug_rewritten')

        items = payload if isinstance(payload, list) else payload.get('items', [])

        updated = []

        for item in items:
            video_id = item.get('video_id')
            title = item.get('title')
            description = item.get('description')

            if not video_id:
                continue

            try:
                video: VideoItem = VideoItem.objects.get(pk=video_id)
            except VideoItem.DoesNotExist:
                continue

            if title:
                video.title_rewritten = title
                video.slug_rewritten = slugify(title)[:field.max_length]
            if description:
                video.description = description
            video.save()

            updated.append(video_id)

        return updated

    def get_videos_for_rewrite(self, limit: int, count: bool, latest: bool) -> dict:
        if latest:
            videos = VideoItem.objects.order_by("-id")
        else:
            videos = (
                VideoItem.objects
                .order_by("-id")
                .filter(slug_rewritten__isnull=True)[:limit]
            )

            VideoItem.objects.filter(
                id__in=list(videos.values_list('id', flat=True)),
                slug_rewritten__isnull=True
            ).update(slug_rewritten="__PROCESSING__")

        counter = VideoItem.objects.filter(slug_rewritten__isnull=False).count() if count else 0

        return {
            "info": {
                "count": counter
            },
            "items": [
                {
                    "video_id": v.id,
                    "title": v.title,
                }
                for v in videos
            ]
        }
