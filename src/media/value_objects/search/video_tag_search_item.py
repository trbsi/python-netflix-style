class VideoTagSearchItem:
    def __init__(self, video_id: int, matched_tags: list[str]):
        self.video_id = video_id
        self.matched_tags = matched_tags
