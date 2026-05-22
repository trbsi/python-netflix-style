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

        # Only aliases with a known group are scored; ungrouped aliases have no
        # weight to contribute so they are excluded entirely.
        tag_aliases: QuerySet[TagAlias] = (
            TagAlias.objects
            .filter(canonical_tag_id__in=canonical_tag_ids)
            .filter(tag_group__isnull=False)
        )

        if not tag_aliases:
            return []

        # raw_tag_metadata — fast lookup when checking which Manticore-returned tags
        #   are part of this query and what their rarity/group is.
        # query_groups — the expected set of tags per group; used as the denominator
        #   when computing how much of a group a video covered.
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

        # Final score is the sum of per-group contributions:
        #   score = Σ_g  weight_g × coverage_g × avg_rarity_g
        #
        # Scoring per group rather than across all tags prevents a large number of
        # low-weight group tags from outscoring a single high-weight group match.
        scored_videos = []
        for video_id, item in result.items.items():
            # Bucket each matched tag into its group so coverage can be computed per group.
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
                # Fraction of this group's query tags the video actually contains.
                group_coverage = len(matched_metas) / len(query_group.tag_aliases)
                # Rarity rewards uncommon tag combinations; averaged so tag count
                # within the group doesn't inflate the score.
                avg_rarity = sum(m.rarity_score for m in matched_metas) / len(matched_metas)
                score += query_group.weight * group_coverage * avg_rarity

            scored_videos.append((video_id, score))

        scored_videos.sort(key=lambda x: x[1], reverse=True)
        return [video_id for video_id, _ in scored_videos[:limit]]
