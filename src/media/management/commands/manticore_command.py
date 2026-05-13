from src.core.management.commands.base_command import BaseCommand
from src.media.services.manticore.manticore_index_service import ManticoreIndexService
from src.media.services.manticore.manticore_schema_service import ManticoreSchemaService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('action', type=str, )

    def handle(self, *args, **options):
        action = options['action']
        schema_service = ManticoreSchemaService()

        if action == 'create_index':
            schema_service.create_indexes()
            print('Indexes created')

        if action == 'reindex':
            schema_service.create_indexes()
            ManticoreIndexService().reindex_all()
            print('Reindexing done')
