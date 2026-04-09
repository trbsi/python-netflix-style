from src.core.management.commands.base_command import BaseCommand
from src.media.services.ai_rewrite.ai_rewrite_service import AiRewriteService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('type', type=str)
        parser.add_argument('batch_size', type=int, nargs='?')

    def handle(self, *args, **options):
        self.info('Start batching')

        type = options['type']
        service = AiRewriteService()

        if type == 'send_to_batch':
            batch_size = int(options['batch_size'])
            service.send_to_batch(batch_size)
            self.info('Finish batching')
        elif type == 'check_batch':
            service.check_and_save_batch_result()
            self.info('Finish checking reults')
