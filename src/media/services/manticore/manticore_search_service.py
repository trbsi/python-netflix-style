from manticoresearch import SearchResponse

from src.media.services.manticore.manticore_base_service import ManticoreBaseService
from src.media.value_objects.search.search_item import SearchItem
from src.media.value_objects.search.search_result import SearchResult


class ManticoreSearchService(ManticoreBaseService):
    # https://manual.manticoresearch.com/Searching/Pagination#Scrolling-via-JSON
    def search_videos(self, search_term: str, scroll: str | None = None, limit: int = 50) -> SearchResult:
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
            items.append(SearchItem(
                id=hit.id,
                title=hit.source['title'],
                slug=hit.source['slug'],
                duration=hit.source['duration'],
                thumbnail=hit.source['thumbnail'],
                categories=hit.source['categories']
            ))

        return SearchResult(result.scroll, items)

    def search_tags(self, tags: list, limit: int = 300) -> list:
        query = {
            "table": self._video_tag_table(),
            "query": {
                "in": {
                    "tag": tags
                }
            },
            "limit": limit
        }

        result: SearchResponse = self.searchApi.search(query)
        hits = result.hits.hits
        video_ids = list(set([hit.source['video_id'] for hit in hits]))
        return video_ids
