from dataclasses import dataclass


@dataclass
class TagAliasMeta:
    rarity_score: float
    tag_group: str
