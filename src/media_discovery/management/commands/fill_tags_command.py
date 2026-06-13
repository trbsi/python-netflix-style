from src.core.management.commands.base_command import BaseCommand
from src.media_discovery.services.raw_tags.raw_tags_service import RawTagsService


class Command(BaseCommand):
    help = "Fill tags table"

    def handle(self, *args, **options):
        RawTagsService().handle_tags()
        self.success(f"Inserted media raw tags")
