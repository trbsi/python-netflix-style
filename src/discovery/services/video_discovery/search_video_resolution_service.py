from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import TagAlias, SearchQuery
from src.discovery.services.video_discovery.value_objects.structured_query_intent import StructuredQueryIntent
from src.manticore.services.manticore.manticore_search_service import ManticoreSearchService
from src.media.value_objects.search.video_structured_match_result import VideoStructuredMatchResult

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
        scores = self._score_direct_results(result, intent)

        return sorted(scores.keys(), key=lambda vid: scores[vid], reverse=True)

    def _score_direct_results(
        self,
        matches: VideoStructuredMatchResult,
        intent: StructuredQueryIntent,
    ) -> dict[int, float]:
        intent_roles = set(intent.roles)
        intent_appearances = set(intent.appearances)
        intent_traits = set(intent.traits)
        intent_interactions = set(intent.interactions)
        intent_settings = set(intent.settings)
        intent_categories = set(intent.categories)

        scores = {}
        for video_id, match in matches.items.items():
            score = 0.0

            if intent_roles:
                score += TagGroupEnum.role.value * len(match.roles & intent_roles) / len(intent_roles)

            if intent_interactions:
                video_interactions = match.acts | match.positions | match.kinks
                score += TagGroupEnum.act.value * len(video_interactions & intent_interactions) / len(intent_interactions)

            if intent_traits:
                score += TagGroupEnum.kink.value * len(match.traits & intent_traits) / len(intent_traits)

            if intent_appearances:
                score += TagGroupEnum.appearance.value * len(match.appearance & intent_appearances) / len(intent_appearances)

            if intent_settings:
                score += TagGroupEnum.setting.value * len(match.setting & intent_settings) / len(intent_settings)

            if intent_categories:
                score += TagGroupEnum.category.value * len(match.categories & intent_categories) / len(intent_categories)

            scores[video_id] = score

        return scores

    def _resolve_intent(self, structured_query: str) -> StructuredQueryIntent:
        chunks = [c.strip() for c in structured_query.split(',') if c.strip()]
        if not chunks:
            return StructuredQueryIntent()

        aliases = (
            TagAlias.objects
            .select_related('canonical_tag')
            .filter(raw_tag__in=chunks, canonical_tag__isnull=False)
            .only('raw_tag', 'canonical_tag__slug', 'canonical_tag__tag_group')
        )

        roles, appearances, traits, interactions, settings, categories = [], [], [], [], [], []

        for alias in aliases:
            group = alias.canonical_tag.tag_group
            slug = alias.raw_tag
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
            elif group == TagGroupEnum.category.name:
                categories.append(slug)

        return StructuredQueryIntent(
            roles=list(dict.fromkeys(roles)),
            appearances=list(dict.fromkeys(appearances)),
            traits=list(dict.fromkeys(traits)),
            interactions=list(dict.fromkeys(interactions)),
            settings=list(dict.fromkeys(settings)),
            categories=list(dict.fromkeys(categories)),
        )
