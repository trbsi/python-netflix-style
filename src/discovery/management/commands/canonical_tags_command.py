from src.core.management.commands.base_command import BaseCommand
from src.discovery.services.canonical_tags.canonical_tags_service import CanonicalTagsService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--steps',
            nargs='+',
            choices=CanonicalTagsService.STEPS,
            default=None,
            metavar='STEP',
            help=f'Steps to run. Choices: {", ".join(CanonicalTagsService.STEPS)}. Defaults to all.',
        )

    def handle(self, *args, **options):
        service = CanonicalTagsService()
        service.extract_tags(steps=options['steps'])
        self.success("Successfully extracted tags")
