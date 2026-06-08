import json
import zlib

from django.db.models import QuerySet
from manticoresearch import DeleteDocumentRequest

from src.core.utils.lang import get_language_codes, get_active_language
from src.discovery.models import TagAlias
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
        video_docs = []
        video_tag_docs = []

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

            # <QuerySet[{'canonical_tag__slug': 'handjob'}, {'canonical_tag__slug': 'hentai-3d-anime'}]>
            raw_tags: QuerySet[dict] = (
                TagAlias.objects
                .prefetch_related('canonical_tag')
                .filter(raw_tag__in=video.categories_and_tags())
                .filter(canonical_tag__isnull=False)
                .values('canonical_tag__slug')
                .distinct()
            )
            category = "gay" if video.has_gay_category() else video.category_slugs()[0]

            for tag in raw_tags:
                canonical = tag['canonical_tag__slug']
                doc_id = zlib.crc32(f"{video.id}:{canonical}".encode())
                video_tag_docs.append({
                    "replace": {
                        "table": self._video_tag_table(lang),
                        "id": doc_id,
                        "doc": {
                            "video_id": video.id,
                            "category": category,
                            "canonical_tag": canonical,
                        }
                    }
                })

        payload = '\n'.join(map(json.dumps, video_docs)) + '\n'
        self.indexApi.bulk(payload)

        payload = '\n'.join(map(json.dumps, video_tag_docs)) + '\n'
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
