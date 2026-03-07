import json

import manticoresearch
from django.db.models import QuerySet

from src.media.models import VideoItem


class ManticoreService:
    def __init__(self):
        # https://manual.manticoresearch.com/Quick_start_guide?client=Python
        config = manticoresearch.Configuration(host="http://manticore:9308")  # docker container name
        client = manticoresearch.ApiClient(config)
        self.utils = manticoresearch.UtilsApi(client)
        self.indexApi = manticoresearch.IndexApi(client)

    # https://manual.manticoresearch.com/Data_creation_and_modification/Updating_documents/REPLACE?client=Python
    def index_single(self, video: VideoItem):
        doc = {
            "table": "videos_index",
            "id": video.id,
            "doc": {
                "title": video.title,
                "thumbnail": video.thumb_large,
                "duration": video.duration,
                "categories": video.categories,
            }
        }

        self.indexApi.replace(doc)

    def reindex(self):
        self.utils.sql("TRUNCATE TABLE videos_index")

        items = []
        batch = 10_000
        for item in VideoItem.objects.all().iterator(batch_size=batch):
            items.append(item)

            if len(items) >= batch:
                self.index_batch(items)
                items.clear()

            if items:
                self.index_batch(items)

    def create_table(self):
        self.utils.sql("""
            CREATE TABLE IF NOT EXISTS videos_index (
            id BIGINT, 
            title TEXT, 
            thumbnail TEXT, 
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
                    "table": "videos_index",
                    "id": v.id,
                    "doc": {
                        "title": v.title,
                        "thumbnail": v.thumb_large,
                        "duration": v.duration,
                        "categories": v.categories,
                    }
                }
            }
            for v in rows
        ]
        self.indexApi.bulk('\n'.join(map(json.dumps, docs)))
