from manticoresearch import SearchResponse, SqlResponse

from src.core.utils.utils import dump_debug
from src.discovery.services.search_tags.dataclass.tag_dataclass import TagDataclass, TagsDataclass
from src.discovery.services.video_discovery.value_objects import CanonicalTagDataclass
from src.manticore.services.manticore.manticore_base_service import ManticoreBaseService
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
                    "tags,categories": search_term
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

    def search_video_tags(
            self,
            tags: list[CanonicalTagDataclass],
            is_gay: bool,
            limit: int = 300,
    ) -> VideoTagSearchResult:
        mandatory_tags = self._unique_tags([
            tag.canonical_tag
            for tag in tags
            if tag.is_mandatory()
        ])
        optional_tags = self._unique_tags([
            tag.canonical_tag
            for tag in tags
            if not tag.is_mandatory()
        ])
        query_tags = self._unique_tags(mandatory_tags + optional_tags)

        if not query_tags:
            return VideoTagSearchResult({})

        tags_sql = self._to_sql_list(query_tags)

        if is_gay:
            category_sql = "category = 'gay'"
        else:
            category_sql = "category != 'gay'"

        mandatory_select_sql = ''
        mandatory_having_sql = ''
        if mandatory_tags:
            mandatory_tags_sql = self._to_sql_list(mandatory_tags)
            mandatory_select_sql = (
                f",\n                SUM(canonical_tag IN ({mandatory_tags_sql})) AS mandatory_tags_count"
            )
            mandatory_having_sql = f"HAVING mandatory_tags_count >= {len(mandatory_tags)}"

        """
        Example:
          SELECT
              video_id,
              COUNT(DISTINCT canonical_tag) AS matched_tags_count,
              SUM(canonical_tag IN ('teen','anal')) AS mandatory_tags_count
          FROM video_tags
          WHERE canonical_tag IN ('teen', 'anal', 'blowjob')
          GROUP BY video_id
          HAVING mandatory_tags_count >= 2
        """
        query = f"""
                    SELECT
                        video_id,
                        COUNT(DISTINCT canonical_tag) AS matched_tags_count
                        {mandatory_select_sql}
                    FROM {self._video_tag_table()}
                    WHERE canonical_tag IN ({tags_sql}) AND {category_sql}
                    GROUP BY video_id
                    {mandatory_having_sql}
                    ORDER BY matched_tags_count DESC
                    LIMIT {limit}
                    """

        dump_debug(query)

        result: SqlResponse = self.utils.sql(
            query,
            raw_response=False,
        )

        hits: list = result.actual_instance.hits['hits']
        video_tags: dict[int, int] = {}
        for hit in hits:
            video_id = int(hit['_source']['video_id'])
            matched_tags_count = int(hit['_source']['matched_tags_count'])
            video_tags[video_id] = matched_tags_count

        matches = {
            video_id: VideoTagSearchItem(
                video_id=video_id,
                matched_tags_count=matched_tags_count,
            )
            for video_id, matched_tags_count in video_tags.items()
        }

        return VideoTagSearchResult(matches)

    def _build_video_tag_search_sql(
            self,
            query_tags: list[str],
            mandatory_tags: list[str],
            is_gay: bool,
            limit: int,
    ) -> str:
        pass

    def _to_sql_list(self, values: list[str]) -> str:
        return ','.join(
            self._quote_sql_string(value)
            for value in values
        )

    def _unique_tags(self, tags: list[str]) -> list[str]:
        return list(dict.fromkeys(tags))

    def _quote_sql_string(self, value: str) -> str:
        escaped = value.replace('\\', '\\\\').replace("'", "\\'")
        return f"'{escaped}'"

    def search_tags(self, tag: str, limit: int = 50) -> TagsDataclass:
        tag = tag.lower()
        result: SqlResponse = self.utils.sql(
            f"""
           SELECT *
            FROM {self.TAGS_ALIAS}
            WHERE MATCH('*{tag}*')
            LIMIT {limit}
            """,
            raw_response=False,
        )

        hits: list = result.actual_instance.hits['hits']
        tags_list: list = []
        for hit in hits:
            tag_id = int(hit['_id'])
            raw_tag = hit['_source']['raw_tag']
            tags_list.append((tag_id, raw_tag))

        return TagsDataclass(
            tags=[
                TagDataclass(
                    id=tag_id,
                    raw_tag=raw_tag,
                )
                for tag_id, raw_tag in tags_list
            ])
