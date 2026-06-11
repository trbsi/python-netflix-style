import json

from django.db.models import QuerySet
from manticoresearch import DeleteDocumentRequest

from src.core.utils.lang import get_language_codes, get_active_language
from src.manticore.services.manticore.manticore_base_service import ManticoreBaseService
from src.media.models import VideoItem


class ManticoreIndexService(ManticoreBaseService):
    # https://manual.manticoresearch.com/Data_creation_and_modification/Updating_documents/REPLACE?client=Python
    # NOT USED
    def index_single(self, video: VideoItem):
        doc = {
            "table": self._video_table(),
            "id": video.id,
            "doc": {
                "title": video.main_title,
                "slug": video.slug,
                "thumbnail": video.thumb_large,
                "duration": video.duration,
                "categories": video.categories,
            }
        }
        self.indexApi.replace(doc)

    def reindex_all(self):
        codes = get_language_codes()
        for code in codes:
            self.utils.sql(f"TRUNCATE TABLE {self._video_table(code)}")

        items = []
        batch = 10_000
        videos = VideoItem.objects.prefetch_related('translations_relation').iterator(chunk_size=batch)
        for item in videos:
            items.append(item)

            if len(items) >= batch:
                self.index_batch(items)
                items.clear()

        if items:
            self.index_batch(items)
            items.clear()

    # https://manual.manticoresearch.com/Data_creation_and_modification/Adding_documents_to_a_table/Adding_documents_to_a_real-time_table?client=Python#Bulk-adding-documents
    # https://manual.manticoresearch.com/Data_creation_and_modification/Updating_documents/REPLACE?client=Python
    def index_batch(self, rows: list[VideoItem] | QuerySet[VideoItem]):
        lang = get_active_language()
        video_docs = []

        if not rows:
            return

        for video in rows:
            translation = None

            if lang != "en":
                translation = video.translations_relation.filter(language_code=lang).first()
                if not translation:
                    continue

            title = video.main_title if lang == "en" else translation.title
            slug = video.slug if lang == "en" else translation.slug

            video_docs.append({
                "replace": {
                    "table": self._video_table(lang),
                    "id": video.id,
                    "doc": {
                        "title": title,
                        "slug": slug,
                        "thumbnail": video.thumb_large,
                        "duration": video.duration,
                        "categories": ', '.join(video.category_slugs()),
                        "tags": video.tags,
                    }
                }
            })

        payload = '\n'.join(map(json.dumps, video_docs)) + '\n'
        self.indexApi.bulk(payload)

    def reindex_structured_all(self):
        self.utils.sql(f"TRUNCATE TABLE {self._video_structured_table()}")

        items = []
        batch = 10_000
        videos = VideoItem.objects.iterator(chunk_size=batch)
        for item in videos:
            items.append(item)

            if len(items) >= batch:
                self.index_structured_batch(items)
                items.clear()

        if items:
            self.index_structured_batch(items)
            items.clear()

    def index_structured_batch(self, rows: list[VideoItem] | QuerySet[VideoItem]):
        if not rows:
            return

        def values(value) -> list[str]:
            if value is None:
                return []

            if isinstance(value, list):
                return [str(item).strip() for item in value if item is not None and str(item).strip()]

            value = str(value).strip()
            return [value] if value else []

        def unique(items: list[str]) -> list[str]:
            return list(dict.fromkeys(items))

        docs = []
        for video in rows:
            metadata = video.video_metadata or {}
            participants = metadata.get("participants", [])
            acts_metadata = metadata.get("acts", [])

            roles = ' '.join(
                role
                for participant in participants
                for role in values(participant.get("role"))
            )
            appearance = ' '.join(
                item
                for participant in participants
                for item in values(participant.get("appearance"))
            )
            traits = ' '.join(
                trait
                for participant in participants
                for trait in values(participant.get("traits"))
            )
            acts = ' '.join(
                act
                for item in acts_metadata
                for act in values(item.get("act"))
            )
            positions = ' '.join(
                position
                for item in acts_metadata
                for position in values(item.get("position"))
            )
            kinks = ' '.join(
                kink
                for item in acts_metadata
                for kink in values(item.get("kink"))
            )
            setting = ' '.join(values(metadata.get("setting")))
            category_slugs = unique(values(metadata.get("category")) + video.category_slugs())
            categories = ', '.join(category_slugs)
            title = video.main_title
            all_text = ' '.join(
                filter(None, [title, roles, appearance, traits, acts, positions, kinks, setting, categories]))

            docs.append({
                "replace": {
                    "table": self._video_structured_table(),
                    "id": video.id,
                    "doc": {
                        "title": title,
                        "roles": roles,
                        "appearance": appearance,
                        "traits": traits,
                        "acts": acts,
                        "positions": positions,
                        "kinks": kinks,
                        "setting": setting,
                        "categories": categories,
                        "all_text": all_text,
                    }
                }
            })

        payload = '\n'.join(map(json.dumps, docs)) + '\n'
        self.indexApi.bulk(payload)

    def delete_by_id(self, id: int) -> None:
        codes = get_language_codes()
        for code in codes:
            document = DeleteDocumentRequest(
                table=self._video_table(code),
                id=id
            )
            self.indexApi.delete(document)

    def delete_by_ids(self, ids: list) -> None:
        for id in ids:
            self.delete_by_id(id)
