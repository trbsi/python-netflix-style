from dataclasses import dataclass, field

from src.discovery.services.video_discovery.value_objects.related_tag_expansion import RelatedTagExpansion


@dataclass
class ExpandedRelatedTags:
    query_tag_ids: set[int]
    query_tag_slugs_by_id: dict[int, str]
    related_tag_ids: set[int]
    related_scores_by_tag_id: dict[int, float]
    expansions_by_query_slug: dict[str, list[RelatedTagExpansion]] = field(default_factory=dict)
