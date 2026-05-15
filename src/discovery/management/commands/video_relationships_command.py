from src.core.management.commands.base_command import BaseCommand
from src.discovery.services.relationships.video_relationships_service import VideoRelationshipsService


class Command(BaseCommand):
    help = "Create relationships between videos and embeddings"

    def handle(self, *args, **options):
        service = VideoRelationshipsService()
        service.generate_relationships()
        self.success("Successfully generated relationships")
