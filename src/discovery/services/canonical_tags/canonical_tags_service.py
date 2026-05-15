import re
from pathlib import Path

from django.db.models import QuerySet

from src.discovery.models import TagAlias, CanonicalTag
from src.media.models import VideoItem


class CanonicalTagsService():
    def extract_tags(self):
        self._extract_raw()
        self._connect_canonical()

    def _extract_raw(self):
        videos: QuerySet[VideoItem] = VideoItem.objects.iterator(chunk_size=1000)
        pattern = re.compile(r'^[a-z0-9]+$')

        all_tags = set()

        for video in videos:
            tags = video.tags.split(',')
            categories = video.categories.split(',')
            total = tags + categories
            for tag in total:
                tag = tag.strip().lower()
                if pattern.fullmatch(tag):
                    all_tags.add(tag)

        # fetch existing tags from DB
        existing = set(TagAlias.objects.values_list('raw_tag', flat=True))

        # only new tags
        new_tags = all_tags - existing
        db_tags = [
            TagAlias(raw_tag=tag)
            for tag in new_tags
        ]
        TagAlias.objects.bulk_create(db_tags)

    def _connect_canonical(self):
        import json

        file = Path(__file__).resolve().parent / 'canonical_tags.json'
        with open(file, 'r') as f:
            json = json.load(f)

        for key, data in json.items():
            for canonical, tags in data.items():
                canonical_tag, created = CanonicalTag.objects.get_or_create(
                    slug=canonical,
                    defaults={'display_name': canonical.title()}
                )
                TagAlias.objects.filter(raw_tag__in=tags).update(canonical_tag=canonical_tag)
