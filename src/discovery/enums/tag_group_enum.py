from enum import Enum


class TagGroupEnum(Enum):
    role = 4.5
    kink = 4
    setting = 3.5
    appearance = 3
    position = 2.5
    act = 2
    category = 1.5
    """
    role           → who,
    kink           → relational structure,
    setting         → where,
    appearance      → what they are,
    position       → sex positions,
    act            → what happens,
    category        → weak fallback label
    """

    @staticmethod
    def keys():
        return list(TagGroupEnum.__members__.keys())
