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
    roles           → who
    kinks/dynamics  → relational structure
    setting         → where
    appearance      → what they are
    positions       → sex positions
    acts            → what happens
    scenario        → how it is presented (NEW, optional)
    categories      → weak fallback label
    """
