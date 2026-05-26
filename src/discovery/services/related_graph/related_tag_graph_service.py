from collections import defaultdict
from itertools import combinations
from typing import Iterable

from django.db import transaction

from src.discovery.models import RelatedTag, TagAlias
from src.media.models import VideoItem


class RelatedTagGraphService:
    """
    Builds a weighted graph of canonical tags that appear together on videos.

    The source video data stores raw tags/categories as comma-separated text, while
    TagAlias maps those raw values to CanonicalTag rows. This builder loads that
    alias map once, streams VideoItem rows in chunks, resolves each video's raw
    tags/categories into a deduplicated set of canonical tag IDs, and counts every
    unordered pair that appears on the same video.

    Each graph edge is stored once in RelatedTag with source_tag_id < target_tag_id.
    For every edge, cooccurrence_count is the number of videos containing both tags.
    score is normalized by each tag's overall video frequency:

        score = cooccurrence_count / (freq(tag_a) * freq(tag_b))
        cooccurrence_count = How many videos contain BOTH A and B together
        freq(tag_a) = How many videos contain tag A
        freq(tag_b) = How many videos contain tag B

    This makes highly common tags less dominant than they would be with raw
    co-occurrence counts alone.

    Small example:
        video 1: A, B
        video 2: A, C
        video 3: A, B, C

        frequencies:
            A=3 videos, B=2 videos, C=2 videos

        resulting RelatedTag edges:
            A-B: cooccurrence_count=2, score=2 / (3 * 2) = 0.333333
            A-C: cooccurrence_count=2, score=2 / (3 * 2) = 0.333333
            B-C: cooccurrence_count=1, score=1 / (2 * 2) = 0.25
    """

    def __init__(self, chunk_size: int = 1000, bulk_batch_size: int = 5000):
        self.chunk_size = chunk_size
        self.bulk_batch_size = bulk_batch_size

    def build_graph(self) -> int:
        # Load raw-tag to canonical-tag mapping once so video iteration does not issue DB queries.
        alias_map = self._load_alias_map()
        tag_frequencies: dict[int, int] = defaultdict(int)
        pair_counts: dict[tuple[int, int], int] = defaultdict(int)

        # Stream videos in chunks to keep memory stable on large datasets.
        videos: Iterable[VideoItem] = (
            VideoItem.objects
            .only('id', 'tags', 'categories')
            .iterator(chunk_size=self.chunk_size)
        )

        for video in videos:
            # Deduplicate canonical tags per video so repeated aliases do not inflate counts.
            canonical_tag_ids = self._canonical_tag_ids_for_video(video, alias_map)
            if not canonical_tag_ids:
                continue

            for tag_id in canonical_tag_ids:
                tag_frequencies[tag_id] += 1

            # combinations() emits unordered pairs from the sorted tag list.
            for source_tag_id, target_tag_id in combinations(canonical_tag_ids, 2):
                pair_counts[(source_tag_id, target_tag_id)] += 1

        edge_count = len(pair_counts)
        # Replace the graph atomically so readers do not see a partially rebuilt table.
        self._replace_related_tags(pair_counts, tag_frequencies)
        return edge_count

    def _load_alias_map(self) -> dict[str, int]:
        # TagAlias stores raw video tags/categories mapped onto CanonicalTag rows.
        aliases = (
            TagAlias.objects
            .filter(canonical_tag__isnull=False)
            .values_list('raw_tag', 'canonical_tag_id')
        )

        return {
            raw_tag.strip().lower(): canonical_tag_id
            for raw_tag, canonical_tag_id in aliases
            if raw_tag and canonical_tag_id
        }

    def _canonical_tag_ids_for_video(self, video: VideoItem, alias_map: dict[str, int]) -> list[int]:
        raw_tags = self._split_tags(video.tags) + self._split_tags(video.categories)
        canonical_tag_ids = {
            alias_map[raw_tag]
            for raw_tag in raw_tags
            if raw_tag in alias_map
        }

        # Sorting guarantees each edge is stored with source_tag_id < target_tag_id.
        return sorted(canonical_tag_ids)

    def _split_tags(self, tags: str | None) -> list[str]:
        if not tags:
            return []

        return [
            tag.strip().lower()
            for tag in tags.split(',')
            if tag.strip()
        ]

    def _related_rows(
            self,
            pair_counts: dict[tuple[int, int], int],
            tag_frequencies: dict[int, int],
    ):
        for (source_tag_id, target_tag_id), cooccurrence_count in pair_counts.items():
            source_frequency = tag_frequencies[source_tag_id]
            target_frequency = tag_frequencies[target_tag_id]
            # Normalize by tag frequencies to reduce dominance from broad/popular tags.
            score = cooccurrence_count / (source_frequency * target_frequency)

            yield RelatedTag(
                source_tag_id=source_tag_id,
                target_tag_id=target_tag_id,
                cooccurrence_count=cooccurrence_count,
                score=score,
            )

    def _replace_related_tags(
            self,
            pair_counts: dict[tuple[int, int], int],
            tag_frequencies: dict[int, int],
    ) -> None:
        with transaction.atomic():
            RelatedTag.objects.all().delete()

            # Materialize rows in bounded batches instead of building a second full list in memory.
            batch = []
            for row in self._related_rows(pair_counts, tag_frequencies):
                batch.append(row)
                if len(batch) >= self.bulk_batch_size:
                    RelatedTag.objects.bulk_create(batch, batch_size=self.bulk_batch_size)
                    batch = []

            if batch:
                RelatedTag.objects.bulk_create(batch, batch_size=self.bulk_batch_size)
