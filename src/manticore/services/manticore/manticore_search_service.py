from manticoresearch import SearchResponse, SqlResponse

from src.core.utils.utils import dump_debug
from src.discovery.services.video_discovery.value_objects.structured_query_intent import StructuredQueryIntent
from src.manticore.services.manticore.manticore_base_service import ManticoreBaseService
from src.media.value_objects.search.video_search_item import VideoSearchItem
from src.media.value_objects.search.video_search_result import VideoSearchResult
from src.media.value_objects.search.video_structured_match import VideoStructuredMatch
from src.media.value_objects.search.video_structured_match_result import VideoStructuredMatchResult


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
            video_id = int(hit['_id'])
            src = hit['_source']
            matches[video_id] = VideoStructuredMatch(
                video_id=video_id,
                roles=self._parse_spaced(src.get('roles')),
                appearance=self._parse_spaced(src.get('appearance')),
                traits=self._parse_spaced(src.get('traits')),
                acts=self._parse_spaced(src.get('acts')),
                positions=self._parse_spaced(src.get('positions')),
                kinks=self._parse_spaced(src.get('kinks')),
                setting=self._parse_spaced(src.get('setting')),
                categories=self._parse_csv(src.get('categories')),
            )

        return VideoStructuredMatchResult(matches)

    def _build_match_expression(self, intent: StructuredQueryIntent) -> str:
        parts = []

        def field_expr(field: str, terms: list[str], op: str = '|') -> str:
            joined = f' {op} '.join(terms)
            expr = f'({joined})' if len(terms) > 1 else joined
            return f'@{field} {expr}'

        if intent.roles:
            parts.append(field_expr('roles', intent.roles, '&'))
        if intent.interactions:
            parts.append(field_expr('acts', intent.interactions))
        if intent.appearances:
            parts.append(field_expr('appearance', intent.appearances))
        if intent.traits:
            parts.append(field_expr('traits', intent.traits))
        if intent.settings:
            parts.append(field_expr('setting', intent.settings))
        if intent.categories:
            parts.append(field_expr('categories', intent.categories))

        return ' '.join(parts)

    def _parse_spaced(self, value: str | None) -> frozenset:
        if not value:
            return frozenset()
        return frozenset(t for t in value.split() if t)

    def _parse_csv(self, value: str | None) -> frozenset:
        if not value:
            return frozenset()
        return frozenset(c.strip() for c in value.split(',') if c.strip())

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
