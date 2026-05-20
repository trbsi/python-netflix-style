import json
import re
from collections import defaultdict
from pathlib import Path

from django.db.models import QuerySet

from automationapp import settings
from src.discovery.models import TagAlias, CanonicalTag
from src.media.models import VideoItem


class CanonicalTagsService():
    def extract_tags(self):
        print('Extracting tags')
        self._extract_raw()
        print('Connecting canonical')
        self._connect_canonical()
        print('Updating rarity scores')
        self._update_rarity_scores()
        print('Extracted uncategorized tags')
        self._extract_uncategorized()

    def _extract_raw(self):
        videos: QuerySet[VideoItem] = VideoItem.objects.iterator(chunk_size=1000)
        pattern = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

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
        file = Path(__file__).resolve().parent / 'canonical_tags.json'
        with open(file, 'r') as f:
            data = json.load(f)

        tags = data['canonical_tags']
        for canonical, data in tags.items():
            canonical_tag, created = CanonicalTag.objects.get_or_create(
                slug=canonical,
                defaults={'display_name': canonical.title()}
            )

            # if there is canonical tag among raw_tag then update canonical_tag to itself
            TagAlias.objects.filter(raw_tag=canonical).update(canonical_tag=canonical_tag)
            for synonym in data['synonyms']:
                (TagAlias.objects
                 .filter(raw_tag=synonym['name'])
                 .update(canonical_tag=canonical_tag, tag_group=synonym['group']))

    def _update_rarity_scores(self):
        tag_counts: dict[str, int] = defaultdict(int)
        total_videos = 0

        for video in VideoItem.objects.only('tags', 'categories').iterator(chunk_size=1000):
            total_videos += 1
            seen: set[str] = set()
            for raw in video.tags.split(',') + video.categories.split(','):
                tag = raw.strip().lower()
                if tag and tag not in seen:
                    tag_counts[tag] += 1
                    seen.add(tag)

        if not total_videos:
            return

        to_update = []
        for alias in TagAlias.objects.all():
            count = tag_counts.get(alias.raw_tag, 0)
            alias.rarity_score = round(total_videos / count, 2)
            to_update.append(alias)

        TagAlias.objects.bulk_update(to_update, ['rarity_score'], batch_size=1000)

    def _extract_uncategorized(self):
        tags = list(TagAlias.objects.filter(canonical_tag__isnull=True).values_list('raw_tag', flat=True))

        with open(settings.BASE_DIR / 'uncategorized_tags.json', 'w') as outfile:
            json.dump(tags, outfile)
