from dataclasses import dataclass, field


@dataclass
class VideoStructuredMatch:
    video_id: int
    roles: frozenset = field(default_factory=frozenset)
    appearance: frozenset = field(default_factory=frozenset)
    traits: frozenset = field(default_factory=frozenset)
    acts: frozenset = field(default_factory=frozenset)
    positions: frozenset = field(default_factory=frozenset)
    kinks: frozenset = field(default_factory=frozenset)
    setting: frozenset = field(default_factory=frozenset)
    categories: frozenset = field(default_factory=frozenset)
