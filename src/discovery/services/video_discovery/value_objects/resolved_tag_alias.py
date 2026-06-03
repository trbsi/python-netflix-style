from dataclasses import dataclass


@dataclass
class ResolvedTagAlias:
    raw_tag: str
    canonical_tag: str
    tag_group: str | None
