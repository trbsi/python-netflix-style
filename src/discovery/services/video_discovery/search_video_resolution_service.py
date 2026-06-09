from src.core.utils.utils import dump_debug
from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import TagAlias, SearchQuery
from src.discovery.services.video_discovery.value_objects.structured_query_intent import StructuredQueryIntent
from src.manticore.services.manticore.manticore_search_service import ManticoreSearchService


class SearchVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()

    def resolve_videos(self, tags: dict | None, limit: int = 300) -> list:
        search: SearchQuery = SearchQuery.objects.filter(uuid=tags['id']).first()
        if not search:
            return []

        intent = self._resolve_intent(search.structured_search_query)

        if not intent.all_tags():
            return []

        result = self._manticore.search_video_structured(intent=intent, limit=limit)

        for video_id in result.get_video_ids():
            dump_debug(f"vid:{video_id}")

        return result.get_video_ids()

    def _resolve_intent(self, structured_query: str) -> StructuredQueryIntent:
        chunks = [c.strip() for c in structured_query.split('|') if c.strip()]
        if not chunks:
            return StructuredQueryIntent()

        aliases = (
            TagAlias.objects
            .select_related('canonical_tag')
            .filter(raw_tag__in=chunks, canonical_tag__isnull=False)
            .only('raw_tag', 'canonical_tag__slug', 'canonical_tag__tag_group')
        )

        roles, appearances, traits, interactions, settings = [], [], [], [], []

        for alias in aliases:
            group = alias.canonical_tag.tag_group
            slug = alias.canonical_tag.slug
            if group == TagGroupEnum.role.name:
                roles.append(slug)
            elif group == TagGroupEnum.appearance.name:
                appearances.append(slug)
            elif group == TagGroupEnum.kink.name:
                traits.append(slug)
            elif group == TagGroupEnum.act.name:
                interactions.append(slug)
            elif group == TagGroupEnum.setting.name:
                settings.append(slug)

        return StructuredQueryIntent(
            roles=list(dict.fromkeys(roles)),
            appearances=list(dict.fromkeys(appearances)),
            traits=list(dict.fromkeys(traits)),
            interactions=list(dict.fromkeys(interactions)),
            settings=list(dict.fromkeys(settings)),
        )
