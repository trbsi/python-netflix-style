import time

import bugsnag

from src.core.management.commands.base_command import BaseCommand
from src.sitemap.services.generate_sitemap.generate_sitemap_service import GenerateSitemapService


class Command(BaseCommand):
    help = "Generate sitemap files (incremental or full)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Regenerate all sitemaps from scratch"
        )
        parser.add_argument(
            "--use-gzip",
            action="store_true",
            help="Store sitemap as gzip or not"
        )

    def handle(self, *args, **options):
        is_full = options["full"]
        use_gzip = options["use_gzip"]
        start = time.time()

        self.info('Starting to generate sitemaps')

        service = GenerateSitemapService()
        service.generate_sitemap(is_full, use_gzip)

        end = time.time()
        minutes = (end - start) / 60

        message = f"GenerateSitemapCommand. Execution time: {minutes:.2f} minutes. "
        if is_full:
            message = message + "Full sitemaps generated."
        else:
            message = message + "Incremental sitemaps generated."

        print(message)
        bugsnag.notify(Exception(message))
