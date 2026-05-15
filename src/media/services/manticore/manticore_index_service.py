import hashlib
import json

from django.db.models import QuerySet
from manticoresearch import DeleteDocumentRequest

from src.core.utils.lang import get_language_codes, get_active_language
from src.media.models import VideoItem
from src.media.services.manticore.manticore_base_service import ManticoreBaseService


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
            self.utils.sql(f"TRUNCATE TABLE {self._video_tag_table(code)}")

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
        docs = []
        for video in rows:
            translation = None

            if lang != "en":
                translation = video.translations_relation.filter(language_code=lang).first()
                if not translation:
                    continue

            title = video.main_title if lang == "en" else translation.title
            slug = video.slug if lang == "en" else translation.slug

            docs.append({
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

            for tag in video.categories_and_tags():
                doc_id = int(hashlib.md5(f"{video.id}:{tag}".encode()).hexdigest()[:15], 16)
                docs.append({
                    "replace": {
                        "table": self._video_tag_table(lang),
                        "id": doc_id,
                        "doc": {
                            "video_id": video.id,
                            "tag": tag,
                        }
                    }
                })

        self.indexApi.bulk('\n'.join(map(json.dumps, docs)))

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
