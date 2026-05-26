from dataclasses import dataclass


@dataclass
class ExpandedRelatedTags:
    query_tag_ids: set[int]
    query_tag_slugs_by_id: dict[int, str]
    related_tag_ids: set[int]
    related_tag_slugs: list[str]
    related_scores_by_tag_id: dict[int, float]
