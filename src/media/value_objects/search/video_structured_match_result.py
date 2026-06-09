from src.media.value_objects.search.video_structured_match import VideoStructuredMatch


class VideoStructuredMatchResult:
    def __init__(self, items: dict[int, VideoStructuredMatch]):
        self.items = items

    def get_video_ids(self) -> list[int]:
        return list(self.items.keys())
