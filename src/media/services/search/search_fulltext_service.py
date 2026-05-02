from src.events.services.save_event.save_event_service import SaveEventService
from src.media.services.manticore.manticore_service import ManticoreService
from src.media.value_objects.search.search_result import SearchResult


class SearchFullTextService:
    def __init__(self):
        self.search_index_service = ManticoreService()

    def search_media(self, query: str, scroll: str | None, session_id: str | None) -> SearchResult:
        SaveEventService.save_search_term(session_id, query)
        return self.search_index_service.search_index(query, scroll)
