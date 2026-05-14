from src.core.management.commands.base_command import BaseCommand
from src.discovery.services.canonical_tags.canonical_tags_service import CanonicalTagsService


class Command(BaseCommand):
    def handle(self, *args, **options):
        service = CanonicalTagsService()
        service.extract_tags()
        self.success("Successfully extracted tags")
