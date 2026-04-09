from src.core.management.commands.base_command import BaseCommand
from src.media.services.ai_rewrite.ai_rewrite_service import AiRewriteService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('batch_size', type=int)

    def handle(self, *args, **options):
        self.info('Start batching')

        batch_size = options['batch_size']

        service = AiRewriteService()
        service.rewrite_title(batch_size)

        self.info('Finish batching')
