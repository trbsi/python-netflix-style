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

        self.info('Importing dump from PH')

        ph_dump_service = PhImportFromDumpService()
        try:
            if settings.APP_ENV == 'production':
                self.info('Importing dump from production')
                ph_dump_service.import_from_dump(options["import_all"])
            else:
                self.info('Importing dump from staging')
                ph_dump_service.import_from_dump_locally()
        except Exception as e:
            self.error('Failed to import dump: {}'.format(e))
            bugsnag.notify(e)

        end = time.time()
        message = (f"ImportDumpCommand. Execution time: {end - start:.2f} seconds")
        print(message)
        bugsnag.notify(Exception(message))
