from dataclasses import dataclass, field

from src.discovery.services.video_discovery.value_objects.tag_alias_dataclass import TagAliasDataclass


@dataclass
class CanonicalTagDataclass:
    weight: float
    tag_group: str
    tag_aliases: list[TagAliasDataclass] = field(default_factory=list)
