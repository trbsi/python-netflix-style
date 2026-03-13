import json

import manticoresearch
from django.db.models import QuerySet
from manticoresearch import SearchResponse, DeleteDocumentRequest

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
        doc = {
            "table": self.VIDEOS_INDEX,
            "id": video.id,
            "doc": {
                "title": video.title,
                "thumbnail": video.thumb_large,
                "duration": video.duration,
                "categories": video.categories,
            }
        }

        self.indexApi.replace(doc)

    def reindex_all(self):
        self.utils.sql(f"TRUNCATE TABLE {self.VIDEOS_INDEX}")

        items = []
        batch = 10_000
        for item in VideoItem.objects.all().iterator(batch_size=batch):
            items.append(item)

            if len(items) >= batch:
                self.index_batch(items)
                items.clear()

        if items:
            self.index_batch(items)
            items.clear()

    def create_index(self):
        self.utils.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.VIDEOS_INDEX} (
            id BIGINT, 
            title TEXT, 
            thumbnail STRING, 
            duration INT, 
            categories TEXT
        )
        """)

    # https://manual.manticoresearch.com/Data_creation_and_modification/Adding_documents_to_a_table/Adding_documents_to_a_real-time_table?client=Python#Bulk-adding-documents
    # https://manual.manticoresearch.com/Data_creation_and_modification/Updating_documents/REPLACE?client=Python
    def index_batch(self, rows: list[VideoItem] | QuerySet[VideoItem]):
        docs = [
            {
                "replace": {
                    "table": self.VIDEOS_INDEX,
                    "id": v.id,
                    "doc": {
                        "title": v.title,
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
    def search_index(self, to_search: str) -> SearchResult:
        query = {
            "table": self.VIDEOS_INDEX,
            "options": {
                "scroll": True
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
                duration=hit.source['duration'],
                thumbnail=hit.source['thumbnail'],
                categories=hit.source['categories']
            ))

        return SearchResult(result.scroll, items)

    def delete_by_id(self, id: int) -> None:
        document = DeleteDocumentRequest(
            table=self.VIDEOS_INDEX,
            id=id
        )
        self.indexApi.delete(document)

    def delete_by_ids(self, ids: list) -> None:
        for id in ids:
            self.delete_by_id(id)
