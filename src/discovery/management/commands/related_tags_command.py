from src.core.management.commands.base_command import BaseCommand
from src.discovery.services.related_graph.related_tag_graph_service import RelatedTagGraphService


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.info('Building...')
        service = RelatedTagGraphService()
        service.build_graph()
        self.success("Successfully built graph")
