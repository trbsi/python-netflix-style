from dataclasses import dataclass, field

from src.discovery.services.video_discovery.tag_alias_meta import TagAliasMeta


@dataclass
class TagGroupMeta:
    weight: float
    tag_aliases: list[TagAliasMeta] = field(default_factory=list)
