from src.core.management.commands.base_command import BaseCommand
from src.media.services.manticore.manticore_service import ManticoreService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('action', type=str, )

    def handle(self, *args, **options):
        action = options['action']
        service = ManticoreService()

        if action == 'create_index':
            service.create_index()
            print('Indexes created')

        if action == 'reindex':
            service.create_index()
            service.reindex_all()
            print('Reindexing done')
