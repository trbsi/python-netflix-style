from collections import defaultdict

from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import TagAlias
from src.discovery.services.video_discovery.legacy.related_tag_expansion_service import RelatedTagExpansionService
from src.discovery.services.video_discovery.legacy.video_semantic_scoring_service import (
    VideoSemanticScoringService,
)
from src.discovery.services.video_discovery.value_objects import (
    ExpandedRelatedTags,
    VideoRankingResult,
    VideoRankingScore,
    TagAliasDataclass, TagGroupDataclass,
)
from src.manticore.services.manticore.manticore_search_service import ManticoreSearchService


class TagVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()
        self._related_expansion = RelatedTagExpansionService()
        self._semantic_scoring = VideoSemanticScoringService()

    def resolve_video_ids_by_tag_slugs(self, tags: dict, limit: int = 300) -> list[int]:
        """Return plain video IDs ranked by tag match score, highest first."""
        return self.resolve_scored_videos_by_tag_slugs(tags, limit).get_video_ids()

    def resolve_scored_videos_by_tag_slugs(self, tags: dict, limit: int = 300) -> VideoRankingResult:
        """Run the full scoring pipeline: expand tags, search directly and via related tags, merge and rank results."""
        expanded_tags = self._related_expansion.expand_tags(
            canonical_tags=tags.get("canonical_tags", []),
        )

        tag_groups = self._resolve_tag_groups(tags)
        query_groups = self._build_query_groups(tag_groups)
        direct_raw_tags = [m.raw_tag for g in query_groups.values() for m in g.tag_aliases]

        if not direct_raw_tags:
            return VideoRankingResult(items=[])

        direct_scores, direct_matched = self._score_direct_results(
            direct_raw_tags, query_groups, limit
        )
        related_scores, related_matched = self._score_related_results(
            expanded_tags, direct_raw_tags, limit
        )

        video_ids = set(direct_scores) | set(related_scores)
        scored_videos = sorted(
            [
                VideoRankingScore(
                    video_id=video_id,
                    direct_score=direct_scores.get(video_id, 0.0),
                    related_score=related_scores.get(video_id, 0.0),
                    final_score=direct_scores.get(video_id, 0.0) + related_scores.get(video_id, 0.0),
                    direct_matched_tags=direct_matched.get(video_id, []),
                    related_matched_tags=related_matched.get(video_id, []),
                )
                for video_id in video_ids
            ],
            key=lambda v: v.final_score,
            reverse=True,
        )

        return VideoRankingResult(items=scored_videos[:limit])

    def _build_query_groups(self, tag_groups: dict[str, list[str]]) -> dict[str, TagGroupDataclass]:
        """Build per-group metadata needed for direct scoring.

        Each group holds its weight and the full list of TagAliasMeta (raw_tag + rarity),
        which serves as the coverage denominator and the set to match against.
        Tags with no alias in the DB are silently dropped.
        """
        all_raw_tags = [tag for group_tags in tag_groups.values() for tag in group_tags]
        rarity_by_raw_tag = {
            alias.raw_tag: alias.rarity_score
            for alias in TagAlias.objects.filter(raw_tag__in=all_raw_tags).only("raw_tag", "rarity_score")
        }

        query_groups: dict[str, TagGroupDataclass] = {}

        for group_name, group_raw_tags in tag_groups.items():
            if group_name not in TagGroupEnum.__members__:
                continue

            query_group = query_groups.setdefault(
                group_name, TagGroupDataclass(weight=TagGroupEnum[group_name].value)
            )

            for raw_tag in group_raw_tags:
                rarity = rarity_by_raw_tag.get(raw_tag)
                if rarity is None:
                    continue
                query_group.tag_aliases.append(TagAliasDataclass(raw_tag=raw_tag, rarity_score=rarity))

        return query_groups

    def _score_direct_results(
            self,
            raw_tags: list[str],
            query_groups: dict[str, TagGroupDataclass],
            limit: int,
    ) -> tuple[dict[int, float], dict[int, list[str]]]:
        """Search Manticore for videos matching raw_tags and score each by group coverage × rarity.

        Final score is the sum of per-group contributions:
          score = Σ_g  weight_g × coverage_g × avg_rarity_g

        Scoring per group rather than across all tags prevents a large number of
        low-weight group tags from outscoring a single high-weight group match.
        Returns (scores_by_video_id, matched_tags_by_video_id).
        """
        result = self._manticore.search_video_tags(tags=raw_tags, is_gay=False, limit=limit)
        scores: dict[int, float] = {}
        matched_tags: dict[int, list[str]] = {}

        for video_id, item in result.items.items():
            matched_set = set(item.matched_tags_count)
            score = 0.0

            for query_group in query_groups.values():
                matched_metas = [m for m in query_group.tag_aliases if m.raw_tag in matched_set]
                if not matched_metas:
                    continue
                group_coverage = len(matched_metas) / len(query_group.tag_aliases)
                avg_rarity = sum(m.rarity_score for m in matched_metas) / len(matched_metas)
                score += query_group.weight * group_coverage * avg_rarity

            if score > 0:
                scores[video_id] = score
                matched_tags[video_id] = item.matched_tags_count

        return scores, matched_tags

    def _score_related_results(
            self,
            expanded_tags: ExpandedRelatedTags,
            direct_raw_tags: list[str],
            limit: int,
    ) -> tuple[dict[int, float], dict[int, list[str]]]:
        """Search for videos matching semantically related tags and score them via semantic similarity.

        Videos with a related_score of 0 are excluded. Returns ({}, {}) when no related tags exist.
        """
        related_result = self._search_related_tags(expanded_tags, direct_raw_tags, limit)
        if not related_result:
            return {}, {}

        all_matched_raw_tags = {
            tag for item in related_result.items.values() for tag in item.matched_tags_count
        }
        canonical_ids_by_raw_tag = self._canonical_ids_by_raw_tag(all_matched_raw_tags)

        scores: dict[int, float] = {}
        matched_tags: dict[int, list[str]] = {}

        for video_id, item in related_result.items.items():
            video_canonical_tag_ids = {
                canonical_ids_by_raw_tag[tag]
                for tag in item.matched_tags_count
                if tag in canonical_ids_by_raw_tag
            }
            semantic_score = self._semantic_scoring.score_semantic(
                video_canonical_tag_ids=video_canonical_tag_ids,
                expanded_tags=expanded_tags,
            )
            if semantic_score.related_score <= 0:
                continue

            scores[video_id] = semantic_score.related_score
            matched_tags[video_id] = [
                tag for tag in item.matched_tags_count
                if canonical_ids_by_raw_tag.get(tag) in semantic_score.related_tag_ids
            ]

        return scores, matched_tags

    def _search_related_tags(self, expanded_tags: ExpandedRelatedTags, direct_raw_tags: list[str], limit: int):
        """Resolve related canonical tag IDs to raw tags (excluding direct ones) and search Manticore.

        Returns None when there are no related tags to search.
        """
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

        return self._manticore.search_video_tags(tags=related_raw_tags, is_gay=False, limit=limit)

    def _canonical_ids_by_raw_tag(self, raw_tags: set[str]) -> dict[str, int]:
        """Map raw tag strings to their canonical tag IDs, skipping any without a canonical tag."""
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
        """Resolve canonical tag slugs to raw tags, grouped by their TagGroup.

        Tags with no group, an unknown group, or duplicate raw tags are excluded.
        """
        if not tags:
            return {}

        canonical_tags = tags.get("canonical_tags", [])

        if not canonical_tags:
            return {}

        aliases = (
            TagAlias.objects
            .select_related("canonical_tag")
            .filter(canonical_tag__slug__in=canonical_tags)
        )

        grouped_tags: dict[str, list[str]] = defaultdict(list)
        seen_tags: set[str] = set()

        for alias in aliases:
            if alias.raw_tag in seen_tags:
                continue

            grouped_tags[alias.canonical_tag.tag_group].append(alias.raw_tag)
            seen_tags.add(alias.raw_tag)

        return dict(grouped_tags)
