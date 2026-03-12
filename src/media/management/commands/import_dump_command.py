import time

import bugsnag

from src.core.management.commands.base_command import BaseCommand
from src.media.services.import_dump.import_from_dump_service import ImportFromDumpService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("site", type=str, help="Site like: eporner, pornhub...")
        parser.add_argument(
            "--import-all",
            action="store_true",
            help="Import full csv"
        )

    def handle(self, *args, **options):
        start = time.time()

        import_all = options["import_all"]
        site = options["site"]
        dump_service = ImportFromDumpService()
        message = ''
        total_imported = 0

        try:
            message = f'Importing dump from production. Import all: {"yes" if import_all else "no"}'
            self.info(message)
            total_imported = dump_service.import_from_dump(site, import_all)
        except Exception as e:
            self.error('Failed to import dump: {}'.format(e))
            bugsnag.notify(e)

        end = time.time()

        minutes = (end - start) / 60
        message = f"ImportDumpCommand. Execution time: {minutes:.2f} minutes. Total imported: {total_imported}." + message
        print(message)
        bugsnag.notify(Exception(message))
