class VideoTagSearchItem:
    def __init__(self, video_id: int, matched_tags_count: int):
        self.video_id = video_id
        self.matched_tags_count = matched_tags_count
