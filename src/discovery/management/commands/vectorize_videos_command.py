from src.core.management.commands.base_command import BaseCommand
from src.discovery.services.vectorization.vectorize_videos_service import VectorizeVideosService


class Command(BaseCommand):
    help = "Test pgvector similarity with sample embeddings"

    def handle(self, *args, **options):
        service = VectorizeVideosService()
        service.vectorize_videos()
        self.success('Done')
