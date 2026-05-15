from src.core.management.commands.base_command import BaseCommand
from src.media.services.manticore.manticore_index_service import ManticoreIndexService
from src.media.services.manticore.manticore_schema_service import ManticoreSchemaService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('action', type=str)
        parser.add_argument('--drop-indexes', action='store_true', default=False)

    def handle(self, *args, **options):
        action = options['action']
        drop_indexes = options['drop_indexes']
        schema_service = ManticoreSchemaService()

        if action == 'create_index':
            schema_service.create_indexes(drop_indexes)
            print('Indexes created')

        if action == 'reindex':
            schema_service.create_indexes(drop_indexes)
            ManticoreIndexService().reindex_all()
            print('Reindexing done')
