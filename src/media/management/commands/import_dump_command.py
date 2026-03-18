import time

import bugsnag

from src.core.management.commands.base_command import BaseCommand
from src.media.services.import_dump.import_from_dump_service import ImportFromDumpService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("site", type=str, help="Site like: eporner, pornhub...")
        parser.add_argument("--zip-url", type=str, help="Url to a zip file")
        parser.add_argument(
            "--import-all",
            action="store_true",
            help="Import full csv"
        )

    # https://www.eporner.com/api/v2/feeds/
    # https://info.xvideos.net/db
    # https://www.pornhub.com/webmasters
    def handle(self, *args, **options):
        start = time.time()

        import_all = options["import_all"]
        site = options["site"]
        zip_url = options["zip_url"]
        message = ''
        total_imported = count_today = 0

        try:
            message = f'Importing dump from production. Import all: {"yes" if import_all else "no"}'
            self.info(message)

            dump_service = ImportFromDumpService()
            [total_imported, count_today] = dump_service.import_from_dump(site, import_all, zip_url)
        except Exception as e:
            self.error('Failed to import dump: {}'.format(e))
            bugsnag.notify(e)

        end = time.time()

        minutes = (end - start) / 60
        message = f"ImportDumpCommand. Execution time: {minutes:.2f} minutes. Total imported: {total_imported}. Imported today: {count_today}. " + message
        print(message)
        bugsnag.notify(Exception(message))
