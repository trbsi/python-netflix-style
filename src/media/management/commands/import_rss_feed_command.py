from src.core.management.commands.base_command import BaseCommand
from src.media.services.rss.ph_rss_service import PhRssService


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.info('Importing from PH')
        rss_service = PhRssService()
        rss_service.read_rss()
