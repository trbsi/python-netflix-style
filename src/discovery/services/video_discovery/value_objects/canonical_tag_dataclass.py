from dataclasses import dataclass, field

from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.services.video_discovery.value_objects.tag_alias_dataclass import TagAliasDataclass


@dataclass
class CanonicalTagDataclass:
    weight: float
    tag_group: str
    canonical_tag: str
    tag_aliases: list[TagAliasDataclass] = field(default_factory=list)

    def is_mandatory(self) -> bool:
        return TagGroupEnum.is_mandatory(self.tag_group)
