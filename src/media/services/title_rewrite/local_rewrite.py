import csv

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
