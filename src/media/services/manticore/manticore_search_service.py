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
            SELECT id, COUNT(*) AS matched_tags_count
            FROM {self._video_tag_table()}
            WHERE tags IN ({tags_sql})
            GROUP BY id
            ORDER BY matched_tags_count DESC
            LIMIT {limit}
            """,
            raw_response=False,
        )

        hits = result.hits.hits
        matches = {
            int(hit.source['id']): VideoTagSearchItem(
                video_id=int(hit.source['id']),
                matched_tags_count=int(hit.source['matched_tags_count']),
            )
            for hit in hits
        }

        return VideoTagSearchResult(matches)
