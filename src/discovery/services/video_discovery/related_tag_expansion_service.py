from django.db.models import Q

from src.discovery.models import CanonicalTag, RelatedTag
from src.discovery.services.video_discovery.value_objects import ExpandedRelatedTags


class RelatedTagExpansionService:
    """
    Expands canonical query tags through the RelatedTag graph.

    RelatedTag rows are undirected and stored once with source_tag_id < target_tag_id.
    This service bulk-loads every edge touching the query tags and projects each row
    into query -> related expansions in memory. That keeps the ranking request to a
    small, fixed number of database queries instead of one query per tag.
    """

    def expand_tags(self, canonical_tags: list[str], max_related_per_tag: int = 50) -> ExpandedRelatedTags:
        canonical_tags = list(
            CanonicalTag.objects
            .filter(slug__in=canonical_tags)
            .values('id', 'slug')
        )

        query_tag_ids = {tag['id'] for tag in canonical_tags}
        query_tag_slugs_by_id = {tag['id']: tag['slug'] for tag in canonical_tags}

        if not query_tag_ids:
            return ExpandedRelatedTags(
                query_tag_ids=set(),
                query_tag_slugs_by_id={},
                related_tag_ids=set(),
                related_scores_by_tag_id={},
            )

        edges = (
            RelatedTag.objects
            .filter(Q(source_tag_id__in=query_tag_ids) | Q(target_tag_id__in=query_tag_ids))
            .select_related('source_tag', 'target_tag')
            .only(
                'source_tag_id',
                'target_tag_id',
                'source_tag__slug',
                'target_tag__slug',
                'score',
            )
            .order_by('-score', '-cooccurrence_count')
        )

        related_tag_ids: set[int] = set()
        related_scores_by_tag_id: dict[int, float] = {}
        expansion_count_by_query_slug: dict[str, int] = {
            slug: 0
            for slug in query_tag_slugs_by_id.values()
        }

        for edge in edges:
            projected_edges: list[tuple[int, str, int, str]] = []

            if edge.source_tag_id in query_tag_ids:
                projected_edges.append((
                    edge.source_tag_id,
                    edge.source_tag.slug,
                    edge.target_tag_id,
                    edge.target_tag.slug,
                ))

            if edge.target_tag_id in query_tag_ids:
                projected_edges.append((
                    edge.target_tag_id,
                    edge.target_tag.slug,
                    edge.source_tag_id,
                    edge.source_tag.slug,
                ))

            for query_tag_id, query_slug, related_tag_id, related_slug in projected_edges:
                # A query tag is already handled by direct scoring and must not also
                # receive a semantic boost through a graph edge to another query tag.
                if related_tag_id in query_tag_ids:
                    continue

                if expansion_count_by_query_slug[query_slug] >= max_related_per_tag:
                    continue

                expansion_count_by_query_slug[query_slug] += 1

                related_tag_ids.add(related_tag_id)
                # If several query tags point at the same related canonical tag,
                # keep the strongest relationship so one video tag contributes once.
                related_scores_by_tag_id[related_tag_id] = max(
                    related_scores_by_tag_id.get(related_tag_id, 0.0),
                    edge.score,
                )

        return ExpandedRelatedTags(
            query_tag_ids=query_tag_ids,
            query_tag_slugs_by_id=query_tag_slugs_by_id,
            related_tag_ids=related_tag_ids,
            related_scores_by_tag_id=related_scores_by_tag_id,
        )
