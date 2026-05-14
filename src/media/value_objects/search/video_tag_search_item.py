class VideoTagSearchItem:
    def __init__(self, video_id: int, tags: list = []):
        self.video_id = video_id
        self.tags = tags

    def add_tag(self, tag: str):
        self.tags.append(tag)
