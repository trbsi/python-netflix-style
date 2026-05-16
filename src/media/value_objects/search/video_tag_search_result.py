from src.media.value_objects.search.video_tag_search_item import VideoTagSearchItem


class VideoTagSearchResult:
    def __init__(self, items: dict[int, VideoTagSearchItem]):
        self.items = items

    def get_sorted_video_ids_by_tag_frequency(self) -> list[int]:
        ranked_videos = sorted(
            (
                (search_item.video_id, len(search_item.tags))
                for video_id, search_item in self.items.items()
            ),
            key=lambda x: x[1],
            reverse=True
        )

        return [video_id for video_id, tag_count in ranked_videos]

    def get_video_ids(self) -> list[int]:
        return [search_item.video_id for video_id, search_item in self.items.items()]
