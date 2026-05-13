from src.events.events import enqueue_search_event
from src.media.services.manticore.manticore_search_service import ManticoreSearchService
from src.media.value_objects.search.search_result import SearchResult


class SearchFullTextService:
    def __init__(self):
        self.search_index_service = ManticoreSearchService()

    def search_media(self, query: str, scroll: str | None, session_id: str | None) -> SearchResult:
        enqueue_search_event(session_id, query)
        return self.search_index_service.search_index(query, scroll)
