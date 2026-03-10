import time

import bugsnag

from automationapp import settings
from src.core.management.commands.base_command import BaseCommand
from src.media.services.import_dump.ph_import_from_dump_service import PhImportFromDumpService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--import-all",
            action="store_true",
            help="Import full csv"
        )

    def handle(self, *args, **options):
        start = time.time()

        import_all = options["import_all"]
        ph_dump_service = PhImportFromDumpService()
        message = ''
        total_imported = 0

        try:
            if settings.APP_ENV == 'production':
                message = f'Importing dump from production. Import all: {'yes' if import_all else 'no'}'
                self.info(message)
                total_imported = ph_dump_service.import_from_dump()
            else:
                message = 'Importing dump from staging'
                self.info(message)
                total_imported = ph_dump_service.import_from_dump_locally()
        except Exception as e:
            self.error('Failed to import dump: {}'.format(e))
            bugsnag.notify(e)

        end = time.time()

        minutes = (end - start) / 60
        message = f"ImportDumpCommand. Execution time: {minutes:.2f} minutes. Total imported: {total_imported}." + message
        print(message)
        bugsnag.notify(Exception(message))
