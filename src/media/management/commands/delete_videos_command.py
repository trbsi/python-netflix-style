import time

import bugsnag

from src.core.management.commands.base_command import BaseCommand
from src.media.services.import_dump.delete_videos_service import DeleteVideosService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("site", type=str, help="Site like: eporner, pornhub...")

    # https://www.eporner.com/api/v2/feeds/
    # https://info.xvideos.net/db
    # https://www.pornhub.com/webmasters
    def handle(self, *args, **options):
        start = time.time()

        site = options["site"]
        delete_service = DeleteVideosService()
        total_deleted = 0

        try:
            self.info('Deleting videos.')
            total_deleted = delete_service.remove_deleted_videos_from_database(site)
        except Exception as e:
            self.error('Failed to delete videos: {}'.format(e))
            bugsnag.notify(e)

        end = time.time()

        minutes = (end - start) / 60
        message = f"DeleteVideosCommand. Execution time: {minutes:.2f} minutes. Total deleted: {total_deleted}."
        print(message)
        bugsnag.notify(Exception(message))
