from dataclasses import dataclass


@dataclass
class TagDataclass:
    id: int
    raw_tag: str


@dataclass
class TagsDataclass:
    tags: list[TagDataclass]

    def to_array(self) -> list:
        return [
            {
                'id': tag.id,
                'raw_tag': tag.raw_tag
            }
            for tag in self.tags
        ]
