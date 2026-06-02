import json

from src.core.management.commands.base_command import BaseCommand
from src.discovery.models.cannonical_tag import CanonicalTag


class Command(BaseCommand):
    help = "Export gay canonical tags grouped by tag_group as JSON"

    def add_arguments(self, parser):
        parser.add_argument('is-gay')

    def handle(self, *args, **options):
        is_gay = options['is-gay']
        tags = CanonicalTag.objects.filter(is_gay=is_gay).values("slug", "tag_group")

        groups = {}
        for tag in tags:
            group = tag["tag_group"] or "ungrouped"
            groups.setdefault(group, []).append(tag["slug"])

        self.stdout.write(json.dumps(groups, indent=2))
