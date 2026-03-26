from src.media.value_objects.search.search_item import SearchItem


class SearchResult:
    def __init__(self, scroll_cursor: str, items: list[SearchItem]):
        self.scroll_cursor = scroll_cursor
        self.items = items

    def to_array(self) -> list:
        array = [item.to_dict() for item in self.items]
        return array
