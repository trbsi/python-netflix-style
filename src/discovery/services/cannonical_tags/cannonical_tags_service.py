from django.db.models import QuerySet

from src.discovery.models import TagAlias
from src.media.models import VideoItem


class CannonicalTagsService():
    def extract_tags(self):
        videos: QuerySet[VideoItem] = VideoItem.objects.iterator(chunk_size=1000)
        for video in videos:
            tags = video.tags.split(',')
            categories = video.categories.split(',')

            tags = set(tags)
            categories = set(categories)
            db_tags = []

            total = tags.union(categories)
            for tag in total:
                db_tags.append(TagAlias(raw_tag=tag))

            TagAlias.objects.bulk_create(db_tags, ignore_conflicts=True)
