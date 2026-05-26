from dataclasses import dataclass


@dataclass
class TagAliasMeta:
    raw_tag: str
    rarity_score: float
