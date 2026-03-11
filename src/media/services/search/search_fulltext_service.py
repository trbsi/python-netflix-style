from src.media.services.manticore.manticore_service import ManticoreService
from src.media.value_objects.search.search_result import SearchResult


class SearchFullTextService:
    def __init__(self):
        self.search_index_service = ManticoreService()

    def search_media(self, query: str) -> SearchResult:
        return self.search_index_service.search_index(query)
