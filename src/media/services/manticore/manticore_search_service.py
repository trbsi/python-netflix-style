from manticoresearch import SearchResponse

from src.media.services.manticore.manticore_base_service import ManticoreBaseService
from src.media.value_objects.search.video_search_item import VideoSearchItem
from src.media.value_objects.search.video_search_result import VideoSearchResult
from src.media.value_objects.search.video_tag_search_item import VideoTagSearchItem
from src.media.value_objects.search.video_tag_search_result import VideoTagSearchResult


class ManticoreSearchService(ManticoreBaseService):
    # https://manual.manticoresearch.com/Searching/Pagination#Scrolling-via-JSON
    def search_videos(self, search_term: str, scroll: str | None = None, limit: int = 50) -> VideoSearchResult:
        query = {
            "table": self._video_table(),
            "options": {
                "scroll": True if scroll is None else scroll,
            },
            "query": {
                "match": {
                    "query": search_term,
                    "fields": ["tags", "categories"],
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},
                {"id": {"order": "asc"}}
            ],
            "track_scores": True,
            "limit": limit
        }
        result: SearchResponse = self.searchApi.search(query)
        hits = result.hits.hits

        items = []
        for hit in hits:
            items.append(VideoSearchItem(
                id=hit.id,
                title=hit.source['title'],
                slug=hit.source['slug'],
                duration=hit.source['duration'],
                thumbnail=hit.source['thumbnail'],
                categories=hit.source['categories']
            ))

        return VideoSearchResult(result.scroll, items)

    def search_tags(self, tags: list, limit: int = 300) -> VideoTagSearchResult:
        tags_sql = ', '.join(
            f"'{tag.replace('\\', '\\\\').replace('\'', '\\\'')}'"
            for tag in tags
        )
        result = self.utils.sql(
            f"""
            SELECT video_id, COUNT(*) AS matched_tags
            FROM {self._video_tag_table()}
            WHERE tag IN ({tags_sql})
            GROUP BY video_id
            ORDER BY matched_tags DESC
            LIMIT {int(limit)}
            """,
            raw_response=False,
        )

        hits = result.actual_instance.hits.get('hits', [])
        matches = {
            int(hit['_source']['video_id']): VideoTagSearchItem(
                video_id=int(hit['_source']['video_id']),
                tags=[None] * int(hit['_source']['matched_tags']),
            )
            for hit in hits
        }

        return VideoTagSearchResult(matches)
