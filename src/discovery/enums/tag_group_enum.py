from enum import Enum


class TagGroupEnum(Enum):
    role = 7
    kink = 6
    setting = 5
    appearance = 4
    position = 3
    act = 2
    category = 1
    """
    role → who,
    kink → relational structure,
    setting → where,
    appearance → what they are,
    position → sex positions,
    act → what happens,
    category → weak fallback label
    """

    @staticmethod
    def keys():
        return list(TagGroupEnum.__members__.keys())

    @staticmethod
    def weight(group: str):
        return TagGroupEnum[group].value

    @staticmethod
    def is_mandatory(group: str) -> bool:
        mandatory = [TagGroupEnum.role.name, TagGroupEnum.appearance.name, TagGroupEnum.position.name]
        return group in mandatory

    @staticmethod
    def is_to_ignore(group: str) -> bool:
        to_ignore = [TagGroupEnum.category.name]
        return group in to_ignore
