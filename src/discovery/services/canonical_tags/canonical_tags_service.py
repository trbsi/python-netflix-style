import re

from django.db.models import QuerySet

from src.discovery.models import TagAlias
from src.media.models import VideoItem


class CanonicalTagsService():
    def extract_tags(self):
        videos: QuerySet[VideoItem] = VideoItem.objects.iterator(chunk_size=1000)
        pattern = re.compile(r'^[a-z0-9]+$')

        all_tags = set()

        for video in videos:
            tags = video.tags.split(',')
            categories = video.categories.split(',')
            total = tags + categories
            for tag in total:
                tag = tag.strip().lower()
                if pattern.fullmatch(tag):
                    all_tags.add(tag)

        # fetch existing tags from DB
        existing = set(TagAlias.objects.values_list('raw_tag', flat=True))

        # only new tags
        new_tags = all_tags - existing
        db_tags = [
            TagAlias(raw_tag=tag)
            for tag in new_tags
        ]
        TagAlias.objects.bulk_create(db_tags)
