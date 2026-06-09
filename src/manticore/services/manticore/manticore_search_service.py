from manticoresearch import SearchResponse, SqlResponse

from src.core.utils.utils import dump_debug
from src.discovery.services.video_discovery.value_objects import CanonicalTagDataclass
from src.discovery.services.video_discovery.value_objects.structured_query_intent import StructuredQueryIntent
from src.manticore.services.manticore.manticore_base_service import ManticoreBaseService
from src.media.value_objects.search.video_search_item import VideoSearchItem
from src.media.value_objects.search.video_search_result import VideoSearchResult
from src.media.value_objects.search.video_structured_match import VideoStructuredMatch
from src.media.value_objects.search.video_structured_match_result import VideoStructuredMatchResult
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

    def search_video_structured(
            self,
            intent: StructuredQueryIntent,
            limit: int = 300,
    ) -> VideoStructuredMatchResult:
        match_expr = self._build_match_expression(intent)
        if not match_expr:
            return VideoStructuredMatchResult({})

        query = f"""
                    SELECT *
                    FROM {self._video_structured_table()}
                    WHERE MATCH('{match_expr}')
                    ORDER BY WEIGHT() DESC
                    LIMIT {limit}
                    """

        dump_debug(query)

        result: SqlResponse = self.utils.sql(query, raw_response=False)
        hits: list = result.actual_instance.hits['hits']

        matches = {}
        for hit in hits:
            src = hit['_source']
            video_id = int(src['video_id'])
            matches[video_id] = VideoStructuredMatch(video_id=video_id)

        return VideoStructuredMatchResult(matches)

    def _build_match_expression(self, intent: StructuredQueryIntent) -> str:
        parts = []

        def field_expr(field: str, terms: list[str]) -> str:
            joined = ' & '.join(terms)
            expr = f'({joined})' if len(terms) > 1 else joined
            return f'@{field} {expr}'

        if intent.roles:
            parts.append(field_expr('roles', intent.roles))
        if intent.interactions:
            parts.append(field_expr('acts', intent.interactions))
        if intent.appearances:
            parts.append(field_expr('appearance', intent.appearances))
        if intent.traits:
            parts.append(field_expr('traits', intent.traits))
        if intent.settings:
            parts.append(field_expr('setting', intent.settings))

        return ' '.join(parts)

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
