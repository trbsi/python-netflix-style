from dataclasses import dataclass


@dataclass(frozen=True)
class RelatedTagExpansion:
    query_tag_id: int
    query_tag_slug: str
    related_tag_id: int
    related_tag_slug: str
    score: float
