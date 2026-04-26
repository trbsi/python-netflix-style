from src.core.management.commands.base_command import BaseCommand
from src.core.services.indexing.indexnow_service import IndexNowService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', default=False, )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        service = IndexNowService()
        service.send_urls_to_indexnow(dry_run)
