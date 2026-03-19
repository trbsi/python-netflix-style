import time

import bugsnag
from django.core.management.base import BaseCommand

from src.sitemap.services.generate_sitemap.generate_sitemap_service import GenerateSitemapService


class Command(BaseCommand):
    help = "Generate sitemap files (incremental or full)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Regenerate all sitemaps from scratch"
        )

    def handle(self, *args, **options):
        start = time.time()

        service = GenerateSitemapService()
        service.generate_sitemap(options["full"])

        end = time.time()
        minutes = (end - start) / 60
        message = f"GenerateSitemapCommand. Execution time: {minutes:.2f} minutes."

        print(message)
        bugsnag.notify(Exception(message))
