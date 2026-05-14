from src.media.value_objects.search.video_search_item import VideoSearchItem


class VideoSearchResult:
    def __init__(self, scroll_cursor: str, items: list[VideoSearchItem]):
        self.scroll_cursor = scroll_cursor
        self.items = items

    def to_array(self) -> list:
        array = [item.to_dict() for item in self.items]
        return array
