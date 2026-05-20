from django.db.models import QuerySet

from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import CanonicalTag, TagAlias
from src.discovery.services.video_discovery.tag_alias_meta import TagAliasMeta
from src.media.services.manticore.manticore_search_service import ManticoreSearchService


class TagVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()

    def resolve_video_ids_by_tag_slugs(self, canonical_tag_slugs: list[str], limit: int = 300) -> list[int]:
        # Resolve canonical tag slugs to their DB primary keys
        canonical_tag_ids = list(
            CanonicalTag.objects
            .filter(slug__in=canonical_tag_slugs)
            .values_list('id', flat=True)
        )

        # Fetch all raw tag aliases that belong to the resolved canonical tags
        tag_aliases: QuerySet[TagAlias] = TagAlias.objects.filter(canonical_tag_id__in=canonical_tag_ids)
        if not tag_aliases:
            return []

        # Build a lookup: raw_tag → TagAliasMeta(group_weight, rarity_score)
        # group_weight comes from TagGroupEnum using the alias's tag_group name;
        # defaults to 1.0 when tag_group is unset or not in the enum
        tag_metadata: dict[str, TagAliasMeta] = {}
        for alias in tag_aliases:
            group_weight = 1.0
            if alias.tag_group:
                group_weight = TagGroupEnum[alias.tag_group].value

            tag_metadata[alias.raw_tag] = TagAliasMeta(
                group_weight=group_weight,
                rarity_score=alias.rarity_score,
            )

        raw_tags = list(tag_metadata.keys())
        # Sum of all tag group weights in the query — denominator for match_quality
        total_query_weight = sum(m.group_weight for m in tag_metadata.values())
        # Total number of raw tags sent to Manticore — denominator for coverage
        total_raw_tags = len(raw_tags)
        # group_weight = sum(group_weight * tags_in_group / total_tags) across all groups
        # e.g. 2 "roles" tags + 1 "setting" + 1 "acts" → roles*2/4 + setting*1/4 + acts*1/4
        # equivalent to total_query_weight / total_raw_tags since each tag contributes its group weight once
        group_weight = total_query_weight / total_raw_tags

        # Query Manticore to find which videos contain any of the raw tags,
        # and get the specific matched tags per video
        result = self._manticore.search_tags(tags=raw_tags, limit=limit)

        # Score each video using:
        #   video_score = group_weight * coverage * match_quality * rarity_score
        scored_videos = []
        for video_id, item in result.items.items():
            matched_meta = []
            for tag in item.matched_tags:
                if tag in tag_metadata:
                    matched_meta.append(tag_metadata[tag])

            if not matched_meta:
                continue

            # coverage = matched tags / total query tags
            coverage = len(item.matched_tags) / total_raw_tags
            # match_quality = sum(matched tag weights) / sum(all query tag weights)
            match_quality = sum(m.group_weight for m in matched_meta) / total_query_weight
            # rarity_score = avg(rarity score of each matched tag)
            rarity_score = sum(m.rarity_score for m in matched_meta) / len(matched_meta)

            score = group_weight * coverage * match_quality * rarity_score
            scored_videos.append((video_id, score))

        scored_videos.sort(key=lambda item: item[1], reverse=True)
        return [video_id for video_id, _ in scored_videos[:limit]]
