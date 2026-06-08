import manticoresearch

from src.core.utils.lang import get_active_language


class ManticoreBaseService:
    VIDEOS_INDEX = 'videos_index'
    VIDEOS_STRUCTURED = 'videos_structured'
    VIDEO_TAGS = 'video_tags'
    TAGS_ALIAS = 'tags_alias'

    def __init__(self):
        config = manticoresearch.Configuration(host="http://manticore:9308")
        client = manticoresearch.ApiClient(config)
        self.utils = manticoresearch.UtilsApi(client)
        self.indexApi = manticoresearch.IndexApi(client)
        self.searchApi = manticoresearch.SearchApi(client)

    def _video_table(self, lang: str | None = None):
        if not lang:
            lang = get_active_language()
        return f'{self.VIDEOS_INDEX}_{lang}'

    def _video_tag_table(self, lang: str | None = None):
        if not lang:
            lang = get_active_language()
        return f'{self.VIDEO_TAGS}_{lang}'

    def _video_structured_table(self, lang: str | None = None):
        if not lang:
            lang = get_active_language()
        return f'{self.VIDEOS_STRUCTURED}_{lang}'
