from django.urls import reverse_lazy

from src.core.utils import unslugify


class SearchItem:
    def __init__(self, id: int, title: str, duration: int, thumbnail: str, categories: str):
        self.id = id
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.categories = categories

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "url": reverse_lazy("media.single_video", kwargs={"id": self.id}),
            "categories": [
                {
                    "title": category.strip(),
                    "slug": unslugify(category.strip()),
                } for category in self.categories.split(', ')
            ]
        }
