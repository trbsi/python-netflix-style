from automationapp import settings
from src.core.management.commands.base_command import BaseCommand
from src.media.services.import_dump.ph_import_from_dump_service import PhImportFromDumpService
from src.media.services.rss.ph_rss_service import PhRssService


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.info('Importing dump from PH')
        ph_dump_service = PhImportFromDumpService()
        if settings.env == 'production':
            ph_dump_service.import_from_dump()
        else:
            ph_dump_service.import_from_dump_locally()
