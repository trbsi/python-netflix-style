from src.media.value_objects.search.search_item import SearchItem


class SearchResult:
    def __init__(self, cursor: str, items: list[SearchItem]):
        self.cursor = cursor
        self.items = items

    def to_array(self) -> list:
        array = [item.to_dict() for item in self.items]
        return array
