from src.media.value_objects.search.video_tag_search_item import VideoTagSearchItem


class VideoTagSearchResult:
    def __init__(self, items: list[VideoTagSearchItem]):
        self.items = items

    def get_sorted_video_ids_by_tag_frequency(self) -> list[int]:
        ranked_videos = sorted(
            (
                (item.video_id, len(item.tags))
                for item in self.items
            ),
            key=lambda x: x[1],
            reverse=True
        )

        return [video_id for video_id, tag_count in ranked_videos]

    def get_video_ids(self) -> list[int]:
        return [item.video_id for item in self.items]
