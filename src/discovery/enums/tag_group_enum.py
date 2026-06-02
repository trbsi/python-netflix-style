from enum import Enum


class TagGroupEnum(Enum):
    roles = 4.5
    kinks = 4
    setting = 3.5
    appearance = 3
    positions = 2.5
    acts = 2
    categories = 1.5
    """
    roles           → who,
    kinks           → relational structure,
    setting         → where,
    appearance      → what they are,
    positions       → sex positions,
    acts            → what happens,
    categories      → weak fallback label
    """

    @staticmethod
    def keys():
        return list(TagGroupEnum.__members__.keys())
