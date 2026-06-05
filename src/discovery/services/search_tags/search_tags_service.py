from src.manticore.services.manticore.manticore_search_service import ManticoreSearchService


class SearchTagsService:
    def __init__(self):
        self.search = ManticoreSearchService()

    def search_tags(self, tag: str) -> list:
        tags = self.search.search_tags(tag)
        return tags.to_array()
