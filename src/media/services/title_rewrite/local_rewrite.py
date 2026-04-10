import csv

from django.utils.text import slugify

from automationapp import settings
from src.media.models import VideoItem


class LocalRewriteService:
    def export_titles(self, limit, chunk_size, filename):
        file_path = settings.BASE_DIR / filename
        print(f"Starting export -> {file_path}")

        queryset = VideoItem.objects.all().order_by("id").values("id", "title")

        if limit:
            queryset = queryset[:limit]

        queryset = queryset.iterator(chunk_size=chunk_size)

        count = 0

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # header
            writer.writerow(["id", "title"])

            for obj in queryset:
                writer.writerow([
                    obj["id"],
                    obj["title"],
                ])

                count += 1

                if count % 100000 == 0:
                    print(f"{count} rows exported...")

        print(f"Done! Exported {count} rows to {file_path}")

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
