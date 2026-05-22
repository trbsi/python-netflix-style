from collections import defaultdict

from django.db.models import QuerySet

from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import CanonicalTag, TagAlias
from src.discovery.services.video_discovery.tag_alias_meta import TagAliasMeta
from src.discovery.services.video_discovery.tag_group_meta import TagGroupMeta
from src.media.services.manticore.manticore_search_service import ManticoreSearchService


class TagVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()

    def resolve_video_ids_by_tag_slugs(self, canonical_tag_slugs: list[str], limit: int = 300) -> list[int]:
        canonical_tag_ids = list(
            CanonicalTag.objects
            .filter(slug__in=canonical_tag_slugs)
            .values_list('id', flat=True)
        )

        tag_aliases: QuerySet[TagAlias] = (
            TagAlias.objects
            .filter(canonical_tag_id__in=canonical_tag_ids)
            .filter(tag_group__isnull=False)
        )

        if not tag_aliases:
            return []

        # Build raw_tag → TagAliasMeta and group → TagGroupMeta lookups simultaneously
        raw_tag_metadata: dict[str, TagAliasMeta] = {}
        query_groups: dict[str, TagGroupMeta] = {}
        for alias in tag_aliases:
            group_name: str = alias.tag_group
            meta = TagAliasMeta(rarity_score=alias.rarity_score, tag_group=group_name)
            raw_tag_metadata[alias.raw_tag] = meta
            if group_name not in query_groups:
                query_groups[group_name] = TagGroupMeta(weight=TagGroupEnum[group_name].value)
            query_groups[group_name].tag_aliases.append(meta)

        raw_tags = list(raw_tag_metadata.keys())

        result = self._manticore.search_tags(tags=raw_tags, limit=limit)

        # Score each video by summing per-group contributions:
        #   score = Σ_g  group_weight_g * (matched_g / query_g) * avg_rarity_g
        #
        # This ensures a high-weight group (e.g. roles=4.5) always outweighs many
        # low-weight group matches regardless of tag count per group.
        scored_videos = []
        for video_id, item in result.items.items():
            matched_by_group: dict[str, list[TagAliasMeta]] = defaultdict(list)
            for tag in item.matched_tags:
                if tag in raw_tag_metadata:
                    meta = raw_tag_metadata[tag]
                    matched_by_group[meta.tag_group].append(meta)

            if not matched_by_group:
                continue

            score = 0.0
            for group_name, query_group in query_groups.items():
                matched_metas = matched_by_group.get(group_name)
                if not matched_metas:
                    continue
                group_coverage = len(matched_metas) / len(query_group.tag_aliases)
                avg_rarity = sum(m.rarity_score for m in matched_metas) / len(matched_metas)
                score += query_group.weight * group_coverage * avg_rarity

            scored_videos.append((video_id, score))

        scored_videos.sort(key=lambda x: x[1], reverse=True)
        return [video_id for video_id, _ in scored_videos[:limit]]
