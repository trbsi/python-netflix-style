import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from src.media.models import VideoItem


class Command(BaseCommand):
    help = "Export VideoItem table to CSV in BASE_DIR with optional row limit"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Number of rows to export (default: all)",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=10000,
            help="DB fetch chunk size",
        )
        parser.add_argument(
            "--filename",
            type=str,
            default="video_items.csv",
            help="Output CSV filename",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        chunk_size = options["chunk_size"]
        filename = options["filename"]

        file_path = settings.BASE_DIR / filename

        self.stdout.write(self.style.NOTICE(
            f"Starting export -> {file_path}"
        ))

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
                    self.stdout.write(f"{count} rows exported...")

        self.stdout.write(self.style.SUCCESS(
            f"Done! Exported {count} rows to {file_path}"
        ))
