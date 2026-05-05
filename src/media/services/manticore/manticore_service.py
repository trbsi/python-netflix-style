import json

import manticoresearch
from django.db.models import QuerySet
from manticoresearch import SearchResponse, DeleteDocumentRequest

from src.core.utils.lang import get_language_codes, get_active_language
from src.media.models import VideoItem
from src.media.value_objects.search.search_item import SearchItem
from src.media.value_objects.search.search_result import SearchResult


class ManticoreService:
    VIDEOS_INDEX = 'videos_index'

    def __init__(self):
        # https://manual.manticoresearch.com/Quick_start_guide?client=Python
        config = manticoresearch.Configuration(host="http://manticore:9308")  # manticore is docker container name
        client = manticoresearch.ApiClient(config)
        self.utils = manticoresearch.UtilsApi(client)
        self.indexApi = manticoresearch.IndexApi(client)
        self.searchApi = manticoresearch.SearchApi(client)

    # https://manual.manticoresearch.com/Data_creation_and_modification/Updating_documents/REPLACE?client=Python
    def index_single(self, video: VideoItem):
        lang = get_active_language()
        doc = {
            "table": f'{self.VIDEOS_INDEX}_{lang}',
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
            table = f'{self.VIDEOS_INDEX}_{code}'
            self.utils.sql(f"TRUNCATE TABLE {table}")

        items = []
        batch = 10_000
        for item in VideoItem.objects.all().iterator(chunk_size=batch):
            items.append(item)

            if len(items) >= batch:
                self.index_batch(items)
                items.clear()

        if items:
            self.index_batch(items)
            items.clear()

    def create_index(self):
        codes = get_language_codes()
        for code in codes:
            table = f'{self.VIDEOS_INDEX}_{code}'
            self.utils.sql(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                id BIGINT, 
                title TEXT, 
                thumbnail STRING, 
                slug STRING, 
                duration INT, 
                categories TEXT
            )
            """)

    # https://manual.manticoresearch.com/Data_creation_and_modification/Adding_documents_to_a_table/Adding_documents_to_a_real-time_table?client=Python#Bulk-adding-documents
    # https://manual.manticoresearch.com/Data_creation_and_modification/Updating_documents/REPLACE?client=Python
    def index_batch(self, rows: list[VideoItem] | QuerySet[VideoItem]):
        lang = get_active_language()
        docs = [
            {
                "replace": {
                    "table": f'{self.VIDEOS_INDEX}_{lang}',
                    "id": v.id,
                    "doc": {
                        "title": v.main_title,
                        "slug": v.slug,
                        "thumbnail": v.thumb_large,
                        "duration": v.duration,
                        "categories": ', '.join(v.category_slugs()),
                    }
                }
            }
            for v in rows
        ]
        self.indexApi.bulk('\n'.join(map(json.dumps, docs)))

    # https://manual.manticoresearch.com/Searching/Pagination#Scrolling-via-JSON
    def search_index(self, to_search: str, scroll: str | None) -> SearchResult:
        lang = get_active_language()
        query = {
            "table": f'{self.VIDEOS_INDEX}_{lang}',
            "options": {
                "scroll": True if scroll is None else scroll,
            },
            "query": {
                "match": {"title": to_search}
            },
            "sort": [
                {"_score": {"order": "desc"}},
                {"id": {"order": "asc"}}
            ],
            "track_scores": True,
            "limit": 50
        }
        result: SearchResponse = self.searchApi.search(query)
        hits = result.hits.hits

        items = []
        for hit in hits:
            items.append(SearchItem(
                id=hit.id,
                title=hit.source['title'],
                slug=hit.source['slug'],
                duration=hit.source['duration'],
                thumbnail=hit.source['thumbnail'],
                categories=hit.source['categories']
            ))

        return SearchResult(result.scroll, items)

    def delete_by_id(self, id: int) -> None:
        codes = get_language_codes()
        for code in codes:
            document = DeleteDocumentRequest(
                table=f'{self.VIDEOS_INDEX}_{code}',
                id=id
            )
            self.indexApi.delete(document)

    def delete_by_ids(self, ids: list) -> None:
        for id in ids:
            self.delete_by_id(id)
