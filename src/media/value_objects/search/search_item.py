from django.urls import reverse_lazy

from src.core.utils import unslugify


class SearchItem:
    def __init__(self, id: int, title: str, slug: str, duration: int, thumbnail: str, categories: str):
        self.id = id
        self.title = title
        self.slug = slug
        self.duration = duration
        self.thumbnail = thumbnail
        self.categories = categories

    def to_dict(self):
        kwargs = {"id": self.id, "slug": self.slug}
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "url": reverse_lazy("media.single_video", kwargs=kwargs),
            "categories": [
                {
                    "title": category.strip(),
                    "slug": unslugify(category.strip()),
                } for category in self.categories.split(', ')
            ]
        }
