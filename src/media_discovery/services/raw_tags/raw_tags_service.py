import json
from pathlib import Path

from src.media.models import VideoItem
from src.media_discovery.models import Tag


class RawTagsService:
    def handle_tags(self):
        self.insert_clean_tags()
        self.insert_new_update_is_in_use()

    def insert_clean_tags(self):
        file = Path(__file__).resolve().parent / 'canonical_tags_gay_cleaned.json'
        with open(file, 'r') as f:
            data = json.load(f)

        create = [
            Tag(name=item, group=group)
            for group, items in data.items()
            for item in items
        ]
        Tag.objects.bulk_create(create, update_conflicts=True, update_fields=['name', 'group'])

    def insert_new_update_is_in_use(self):
        BATCH_SIZE = 1000
        tags: list = []

        def _flush(tags: list[str]) -> None:
            tags = [tag.lower() for tag in tags]

            Tag.objects.bulk_create([
                Tag(
                    name=tag,
                    group='no_group',
                )
                for tag in tags
            ], ignore_conflicts=True, batch_size=BATCH_SIZE)

        def _as_tags(value) -> list[str]:
            if value is None:
                return []

            if isinstance(value, list):
                return [
                    str(item).strip().lower()
                    for item in value
                    if item is not None and str(item).strip()
                ]

            value = str(value).strip().lower()
            return [value] if value else []

        def _extract_metadata_tags(metadata: dict | None) -> set[str]:
            if not metadata:
                return set()

            tags = set()

            for participant in metadata.get('participants', []):
                if not isinstance(participant, dict):
                    continue

                tags.update(_as_tags(participant.get('role')))
                tags.update(_as_tags(participant.get('appearance')))

            for act in metadata.get('acts', []):
                if not isinstance(act, dict):
                    continue

                tags.update(_as_tags(act.get('act')))
                tags.update(_as_tags(act.get('position')))
                tags.update(_as_tags(act.get('kink')))

            tags.update(_as_tags(metadata.get('setting')))
            tags.update(_as_tags(metadata.get('category')))

            return {tag for tag in tags}

        for video in VideoItem.objects.only('video_metadata').iterator(chunk_size=BATCH_SIZE):
            for tag in _extract_metadata_tags(video.video_metadata):
                tags.append(tag)

        for index in range(0, len(tags), BATCH_SIZE):
            batch = tags[index:index + BATCH_SIZE]
            _flush(batch)

        Tag.objects.update(is_in_use=False)
        for index in range(0, len(tags), BATCH_SIZE):
            Tag.objects.filter(raw_tag__in=tags[index:index + BATCH_SIZE]).update(is_in_use=True)
