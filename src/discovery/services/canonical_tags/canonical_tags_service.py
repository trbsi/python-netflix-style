import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from automationapp import settings
from src.discovery.models import TagAlias, CanonicalTag, RelatedTag
from src.media.models import VideoItem


class CanonicalTagsService():
    STEPS = [
        'extract_raw',
        'connect_canonical',
        'update_rarity_scores',
        'insert_related_tags',
        'extract_uncategorized',
    ]

    def extract_tags(self, steps=None):
        step_map = {
            'extract_raw': (self._extract_raw, 'Extract raw tags'),
            'connect_canonical': (self._connect_canonical, 'Connecting canonicals'),
            'update_rarity_scores': (self._update_rarity_scores, 'Updating rarity scores'),
            'extract_uncategorized': (self._extract_uncategorized, 'Extracting uncategorized'),
        }
        for key in (steps or self.STEPS):
            fn, title = step_map[key]
            print(title)
            fn()

    def _extract_raw(self):
        pattern = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
        BATCH_SIZE = 1000
        tag_counts: dict[str, int] = defaultdict(int)

        def _flush(tags: list[str]) -> None:
            existing_aliases = {
                alias.raw_tag: alias
                for alias in TagAlias.objects.filter(raw_tag__in=tags)
            }
            new = set(tags) - set(existing_aliases)
            if new:
                TagAlias.objects.bulk_create([
                    TagAlias(
                        raw_tag=tag,
                        occurrence_count=tag_counts[tag],
                    )
                    for tag in new
                ], batch_size=BATCH_SIZE)

            to_update = []
            for tag, alias in existing_aliases.items():
                alias.occurrence_count = tag_counts[tag]
                to_update.append(alias)

            if to_update:
                TagAlias.objects.bulk_update(
                    to_update,
                    ['occurrence_count', 'categories'],
                    batch_size=BATCH_SIZE,
                )

        for video in VideoItem.objects.only('tags', 'categories').iterator(chunk_size=BATCH_SIZE):
            for tag in video.tags.split(','):
                if pattern.fullmatch(tag):
                    tag_counts[tag] += 1

        tags = list(tag_counts)
        for index in range(0, len(tags), BATCH_SIZE):
            _flush(tags[index:index + BATCH_SIZE])

    def _connect_canonical(self):
        files = ['canonical_tags_straight.json', 'canonical_tags_gay.json']
        for file_name in files:
            file = Path(__file__).resolve().parent / file_name
            with open(file, 'r') as f:
                data = json.load(f)

            tags = data['canonical_tags']
            for canonical, data in tags.items():
                if 'group' not in data:
                    print(f'Group does not exist for {canonical}')
                    group = None
                else:
                    group = data['group']
                canonical_tag, created = CanonicalTag.objects.update_or_create(
                    slug=canonical,
                    defaults={
                        'display_name': canonical.title(),
                        'tag_group': group,
                        'is_gay': True if file_name == 'canonical_tags_gay.json' else False,
                    }
                )

                # if there is canonical tag among raw_tag then update canonical_tag to itself
                TagAlias.objects.filter(raw_tag=canonical).update(canonical_tag=canonical_tag)

                for synonym in data['synonyms']:
                    (TagAlias.objects
                     .filter(raw_tag=synonym)
                     .update(canonical_tag=canonical_tag))

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
        time = datetime(2026, 5, 28, 0, 0, 0)
        id = TagAlias.objects.filter(canonical_tag__isnull=False).order_by('-id').first().id

        tags = list(
            TagAlias.objects
            # .filter(id__gte=id)
            .filter(created_at__gte=time)
            .filter(canonical_tag__isnull=True)
            .order_by('id')
            .values_list('raw_tag', flat=True)
        )

        with open(settings.BASE_DIR / 'uncategorized_tags.json', 'w') as outfile:
            json.dump(tags, outfile)
