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

            if not video_id or not title:
                continue

            try:
                video: VideoItem = VideoItem.objects.get(pk=video_id)
            except VideoItem.DoesNotExist:
                continue

            video.title_rewritten = title
            video.slug_rewritten = slugify(title)[:field.max_length]
            video.save()

            updated.append(video_id)

        return updated

    def get_videos_for_rewrite(self, limit: int, count: bool | None) -> dict:
        videos = (
            VideoItem.objects
            .order_by("-id")
            .filter(slug_rewritten__isnull=True)[:limit]
        )

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
