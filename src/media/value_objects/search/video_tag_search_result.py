from src.media.value_objects.search.video_tag_search_item import VideoTagSearchItem


class VideoTagSearchResult:
    def __init__(self, items: dict[int, VideoTagSearchItem]):
        self.items = items

    def get_video_ids(self) -> list[int]:
        return [search_item.video_id for video_id, search_item in self.items.items()]
