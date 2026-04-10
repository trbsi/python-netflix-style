from src.core.management.commands.base_command import BaseCommand
from src.media.services.title_rewrite.ai_rewrite_service import AiRewriteService
from src.media.services.title_rewrite.local_rewrite import LocalRewriteService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('type', type=str)
        parser.add_argument('batch_size', type=int, nargs='?')

    def handle(self, *args, **options):
        self.info('Start batching')

        type = options['type']
        ai_service = AiRewriteService()
        local_service = LocalRewriteService()

        if type == 'send_to_batch':
            batch_size = int(options['batch_size'])
            ai_service.send_to_batch(batch_size)
            self.info('Finish batching')
        elif type == 'check_batch':
            ai_service.check_and_save_batch_result()
            self.info('Finish checking reults')
        elif type == 'local_rewrite':
            local_service.local_rewrite()
