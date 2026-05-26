from dataclasses import dataclass, field


@dataclass
class VideoSemanticScore:
    related_score: float
    related_tag_ids: set[int] = field(default_factory=set)
