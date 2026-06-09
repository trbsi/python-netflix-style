from dataclasses import dataclass, field


@dataclass
class StructuredQueryIntent:
    roles: list[str] = field(default_factory=list)
    appearances: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    interactions: list[str] = field(default_factory=list)
    settings: list[str] = field(default_factory=list)

    def all_tags(self) -> list[str]:
        return list(dict.fromkeys(
            self.roles + self.appearances + self.traits + self.interactions + self.settings
        ))
