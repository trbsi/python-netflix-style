from collections import defaultdict

from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import TagAlias
from src.discovery.services.video_discovery.related_tag_expansion_service import RelatedTagExpansionService
from src.discovery.services.video_discovery.value_objects import (
    ExpandedRelatedTags,
    VideoRankingResult,
    VideoRankingScore,
    TagAliasMeta,
    TagGroupMeta
)
from src.discovery.services.video_discovery.video_semantic_scoring_service import (
    VideoSemanticScoringService,
)
from src.media.services.manticore.manticore_search_service import ManticoreSearchService


class TagVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()
        self._related_expansion = RelatedTagExpansionService()
        self._semantic_scoring = VideoSemanticScoringService()

    def resolve_video_ids_by_tag_slugs(self, tags: dict, limit: int = 300) -> list[int]:
        return self.resolve_scored_videos_by_tag_slugs(tags, limit).get_video_ids()

    def resolve_scored_videos_by_tag_slugs(self, tags: dict, limit: int = 300) -> VideoRankingResult:
        expanded_tags = self._related_expansion.expand(
            canonical_tags=tags.get("canonical_tags", []),
        )

        tags = self._resolve_tag_groups(tags)
        raw_tags = [
            raw_tag
            for tag_group, raw_tags in tags.items()
            for raw_tag in raw_tags
        ]

        if not raw_tags:
            return VideoRankingResult(items=[], expanded_related_tags=expanded_tags.expansions_by_query_slug)

        tag_aliases_by_raw_tag = {
            alias.raw_tag: alias
            for alias in TagAlias.objects.filter(raw_tag__in=raw_tags).only(
                "raw_tag",
                "rarity_score",
            )
        }

        # raw_tag_metadata — fast lookup when checking which Manticore-returned tags
        #   are part of this query and what their rarity/group is.
        # query_groups — the expected set of tags per group; used as the denominator
        #   when computing how much of a group a video covered.
        raw_tag_metadata: dict[str, TagAliasMeta] = {}
        query_groups: dict[str, TagGroupMeta] = {}
        for group_name, group_raw_tags in tags.items():
            if group_name not in TagGroupEnum.__members__:
                continue

            if group_name not in query_groups:
                query_groups[group_name] = TagGroupMeta(weight=TagGroupEnum[group_name].value)

            for raw_tag in group_raw_tags:
                alias = tag_aliases_by_raw_tag.get(raw_tag)
                if not alias:
                    continue

                meta = TagAliasMeta(rarity_score=alias.rarity_score, tag_group=group_name)
                raw_tag_metadata[raw_tag] = meta
                query_groups[group_name].tag_aliases.append(meta)

        raw_tags = list(raw_tag_metadata.keys())

        if not raw_tags:
            return VideoRankingResult(items=[], expanded_related_tags=expanded_tags.expansions_by_query_slug)

        direct_result = self._manticore.search_tags(tags=raw_tags, limit=limit)

        # Final score is the sum of per-group contributions:
        #   score = Σ_g  weight_g × coverage_g × avg_rarity_g
        #
        # Scoring per group rather than across all tags prevents a large number of
        # low-weight group tags from outscoring a single high-weight group match.
        direct_scores_by_video_id: dict[int, float] = {}
        direct_matched_tags_by_video_id: dict[int, list[str]] = {}
        for video_id, item in direct_result.items.items():
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

            direct_scores_by_video_id[video_id] = score
            direct_matched_tags_by_video_id[video_id] = item.matched_tags

        related_result = self._search_related_tags(expanded_tags, raw_tags, limit)
        related_scores_by_video_id: dict[int, float] = {}
        related_matched_tags_by_video_id: dict[int, list[str]] = {}

        if related_result:
            related_raw_tags = {
                tag
                for item in related_result.items.values()
                for tag in item.matched_tags
            }
            canonical_ids_by_raw_tag = self._canonical_ids_by_raw_tag(related_raw_tags)

            for video_id, item in related_result.items.items():
                video_canonical_tag_ids = {
                    canonical_ids_by_raw_tag[tag]
                    for tag in item.matched_tags
                    if tag in canonical_ids_by_raw_tag
                }
                semantic_score = self._semantic_scoring.score_semantic(
                    video_canonical_tag_ids=video_canonical_tag_ids,
                    expanded_tags=expanded_tags,
                )

                if semantic_score.related_score <= 0:
                    continue

                related_scores_by_video_id[video_id] = semantic_score.related_score
                related_matched_tags_by_video_id[video_id] = [
                    tag
                    for tag in item.matched_tags
                    if canonical_ids_by_raw_tag.get(tag) in semantic_score.related_tag_ids
                ]

        video_ids = set(direct_scores_by_video_id) | set(related_scores_by_video_id)
        scored_videos = [
            VideoRankingScore(
                video_id=video_id,
                direct_score=direct_scores_by_video_id.get(video_id, 0.0),
                related_score=related_scores_by_video_id.get(video_id, 0.0),
                final_score=(
                        direct_scores_by_video_id.get(video_id, 0.0)
                        + related_scores_by_video_id.get(video_id, 0.0)
                ),
                direct_matched_tags=direct_matched_tags_by_video_id.get(video_id, []),
                related_matched_tags=related_matched_tags_by_video_id.get(video_id, []),
            )
            for video_id in video_ids
        ]

        scored_videos.sort(key=lambda item: item.final_score, reverse=True)

        return VideoRankingResult(
            items=scored_videos[:limit],
            expanded_related_tags=expanded_tags.expansions_by_query_slug,
        )

    def _search_related_tags(self, expanded_tags: ExpandedRelatedTags, direct_raw_tags: list[str], limit: int):
        if not expanded_tags.related_tag_ids:
            return None

        related_raw_tags = list(
            TagAlias.objects
            .filter(canonical_tag_id__in=expanded_tags.related_tag_ids)
            .exclude(raw_tag__in=direct_raw_tags)
            .values_list('raw_tag', flat=True)
        )

        if not related_raw_tags:
            return None

        return self._manticore.search_tags(tags=related_raw_tags, limit=limit)

    def _canonical_ids_by_raw_tag(self, raw_tags: set[str]) -> dict[str, int]:
        if not raw_tags:
            return {}

        return {
            raw_tag: canonical_tag_id
            for raw_tag, canonical_tag_id in (
                TagAlias.objects
                .filter(raw_tag__in=raw_tags, canonical_tag__isnull=False)
                .values_list('raw_tag', 'canonical_tag_id')
            )
        }

    def _resolve_tag_groups(self, tags: dict) -> dict[str, list[str]]:
        if not tags:
            return {}

        canonical_tags = tags.get("canonical_tags", [])

        if not canonical_tags:
            return {}

        aliases = (
            TagAlias.objects
            .filter(canonical_tag__slug__in=canonical_tags)
            .exclude(tag_group__isnull=True)
            .only("raw_tag", "tag_group")
        )

        grouped_tags: dict[str, list[str]] = defaultdict(list)
        seen_tags: set[str] = set()

        for alias in aliases:
            if alias.tag_group not in TagGroupEnum.__members__:
                continue

            if alias.raw_tag in seen_tags:
                continue

            grouped_tags[alias.tag_group].append(alias.raw_tag)
            seen_tags.add(alias.raw_tag)

        return dict(grouped_tags)
