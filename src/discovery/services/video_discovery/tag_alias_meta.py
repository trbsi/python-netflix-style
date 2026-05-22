class TagAliasMeta:
    def __init__(self, group_weight: float, rarity_score: float, tag_group: str | None = None):
        self.group_weight = group_weight
        self.rarity_score = rarity_score
        self.tag_group = tag_group
