from src.discovery.models import CanonicalTag, TagAlias
from src.media.services.manticore.manticore_search_service import ManticoreSearchService


class TagVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()

    def resolve_video_ids_by_tag_slugs(self, canonical_tag_slugs: list[str], limit: int = 300) -> list[int]:
        canonical_tag_ids = (
            CanonicalTag.objects
            .filter(slug__in=canonical_tag_slugs)
            .values_list('id', flat=True)
        )
        raw_tags = list(
            TagAlias.objects
            .filter(canonical_tag_id__in=canonical_tag_ids)
            .values_list('raw_tag', flat=True)
            .distinct()
        )
        if not raw_tags:
            return []

        result = self._manticore.search_tags(tags=raw_tags, limit=limit)
        return result.get_video_ids()
