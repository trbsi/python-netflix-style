import json
import re
from collections import defaultdict
from pathlib import Path

from django.db.models import QuerySet

from automationapp import settings
from src.discovery.models import TagAlias, CanonicalTag, RelatedTag
from src.media.models import VideoItem


class CanonicalTagsService():
    def extract_tags(self):
        print('Extracting tags')
        self._extract_raw()
        print('Connecting canonical')
        self._connect_canonical()
        print('Updating rarity scores')
        self._update_rarity_scores()
        print('Insert related tags')
        self._insert_related_tags()
        print('Extracted uncategorized tags')
        self._extract_uncategorized()

    def _extract_raw(self):
        pattern = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
        BATCH_SIZE = 1000
        batch: set[str] = set()

        def _flush(tags: set[str]) -> None:
            existing = set(TagAlias.objects.filter(raw_tag__in=tags).values_list('raw_tag', flat=True))
            new = tags - existing
            if new:
                TagAlias.objects.bulk_create([TagAlias(raw_tag=t) for t in new], batch_size=BATCH_SIZE)

        for video in VideoItem.objects.only('tags', 'categories').iterator(chunk_size=BATCH_SIZE):
            for raw in video.tags.split(',') + video.categories.split(','):
                tag = raw.strip().lower()
                if pattern.fullmatch(tag):
                    batch.add(tag)

            if len(batch) >= BATCH_SIZE:
                _flush(batch)
                batch.clear()

        if batch:
            _flush(batch)

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
        id = TagAlias.objects.filter(canonical_tag__isnull=False).order_by('-id').first().id

        tags = list(
            TagAlias.objects
            .filter(id__gte=id)
            .filter(canonical_tag__isnull=True)
            .order_by('id')
            .values_list('raw_tag', flat=True)
        )

        with open(settings.BASE_DIR / 'uncategorized_tags.json', 'w') as outfile:
            json.dump(tags, outfile)

    def _insert_related_tags(self):
        RelatedTag.objects.all().delete()

        path = Path(__file__).resolve().parent / 'related_tags.json'
        with open(path, 'r') as outfile:
            data = json.load(outfile)

        for canonical_tag, related_tags in data['related_tags'].items():
            canonical = CanonicalTag.objects.get(slug=canonical_tag)
            for tag in related_tags:
                score = tag['score']
                db_tag = CanonicalTag.objects.get(slug=tag['tag'])
                RelatedTag.objects.create(
                    source_tag=canonical,
                    target_tag=db_tag,
                    score=score,
                )
