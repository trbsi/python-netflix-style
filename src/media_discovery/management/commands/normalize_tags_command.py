from src.core.management.commands.base_command import BaseCommand
from src.media_discovery.services.json_to_normalized.json_to_normalized_tags_service import JsonToNormalizedTagsService


class Command(BaseCommand):
    help = "Insert normalized tags"

    def handle(self, *args, **options):
        JsonToNormalizedTagsService().insert_normalized_tags()
        self.success(f"Inserted normalized tags")
