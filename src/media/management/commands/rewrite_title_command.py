from src.core.management.commands.base_command import BaseCommand
from src.media.services.title_rewrite.ai_rewrite_service import AiRewriteService
from src.media.services.title_rewrite.local_rewrite import LocalRewriteService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('type', type=str)
        parser.add_argument('--batch_size', type=int, default=None)
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Number of rows to export (default: all)",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=10000,
            help="DB fetch chunk size",
        )
        parser.add_argument(
            "--filename",
            type=str,
            default="video_items.csv",
            help="Output CSV filename",
        )

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
        elif type == 'export_titles':
            limit = options["limit"]
            chunk_size = options["chunk_size"]
            filename = options["filename"]
            local_service.export_titles(limit, chunk_size, filename)
