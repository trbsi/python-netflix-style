from collections import defaultdict

import spacy
from spacy.cli import download

from src.core.utils.utils import dump_debug
from src.discovery.enums.tag_group_enum import TagGroupEnum
from src.discovery.models import TagAlias, SearchQuery
from src.discovery.services.video_discovery.legacy.related_tag_expansion_service import RelatedTagExpansionService
from src.discovery.services.video_discovery.legacy.video_semantic_scoring_service import (
    VideoSemanticScoringService,
)
from src.discovery.services.video_discovery.value_objects import (
    VideoRankingResult,
    VideoRankingScore,
    ResolvedTagAlias,
    TagAliasMeta,
    TagGroupMeta,
)
from src.media.services.manticore.manticore_search_service import ManticoreSearchService


class SearchVideoResolutionService:
    def __init__(self):
        self._manticore = ManticoreSearchService()
        self._related_expansion = RelatedTagExpansionService()
        self._semantic_scoring = VideoSemanticScoringService()

    def resolve_videos(self, tags: dict | None, limit: int = 300) -> list:
        search: SearchQuery = SearchQuery.objects.filter(uuid=tags['id']).first()
        if not search:
            return VideoRankingResult(items=[]).get_video_ids()

        """
        example: "black guy,cums,in,twink's ass"
        """
        grouped_query = search.structured_search_query
        grouped_words = self._to_tokens(grouped_query)
        is_gay = 'gay' in search.raw_search_query
        dump_debug(grouped_words)
        resolved_tags = self._resolve_tag_aliases(grouped_words)
        dump_debug(resolved_tags)

        video_ids = []
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

    def _build_query_groups(self, tag_groups: dict[str, list[str]]) -> dict[str, TagGroupMeta]:
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

        query_groups: dict[str, TagGroupMeta] = {}

        for group_name, group_raw_tags in tag_groups.items():
            if group_name not in TagGroupEnum.__members__:
                continue

            query_group = query_groups.setdefault(
                group_name, TagGroupMeta(weight=TagGroupEnum[group_name].value)
            )

            for raw_tag in group_raw_tags:
                rarity = rarity_by_raw_tag.get(raw_tag)
                if rarity is None:
                    continue
                query_group.tag_aliases.append(TagAliasMeta(raw_tag=raw_tag, rarity_score=rarity))

        return query_groups

    def _resolve_tag_aliases(self, raw_tags: list[str]) -> list[ResolvedTagAlias]:
        result = []
        for raw_tag in raw_tags:
            dump_debug(raw_tag)
            alias: TagAlias | None = (
                TagAlias.objects
                .select_related("canonical_tag")
                .filter(
                    raw_tag=raw_tag,
                    canonical_tag__isnull=False,
                )
                .first()
            )

            if not alias:
                continue

            result.append(ResolvedTagAlias(
                raw_tag=alias.raw_tag,
                canonical_tag=alias.canonical_tag.slug,
                tag_group=alias.canonical_tag.tag_group,
            ))

        return result

    def _to_tokens(self, grouped_query: str) -> list[str]:
        model_name = 'en_core_web_sm'
        try:
            nlp = spacy.load(model_name)
        except OSError:
            download(model_name)
            nlp = spacy.load(model_name)

        tokens = []
        groups = [
            group.strip() for group in grouped_query.split(',')
            if group.strip() and group != 'gay'
        ]

        for group in groups:
            doc = nlp(group)
            filtered = [
                (token.text, token.lemma_)
                for token in doc
                if not token.is_stop and token.text.strip()
            ]

            original_words = [t[0] for t in filtered]
            lemma_words = [t[1] for t in filtered]

            tokens.extend(self.make_ngrams(original_words))
            tokens.extend(self.make_ngrams(lemma_words))

        return list(dict.fromkeys(tokens))

    def make_ngrams(self, words: list) -> list:
        # This function generates all forward-combination n-grams (not just adjacent ones)
        # It builds:
        # - 1-grams: single words
        # - 2-grams: all pairs where i < j
        # - 3-grams: all triplets where i < j < k

        ngrams = []

        # -------------------------
        # 1-grams (unigrams)
        # -------------------------
        # Each word is kept as-is
        if len(words) == 1:
            ngrams.extend(words)

        # -------------------------
        # 2-grams (bigrams)
        # -------------------------
        # Create all combinations of two words where the second word comes after the first
        # Example: [a, b, c] → a-b, a-c, b-c
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                ngrams.append(f"{words[i]}-{words[j]}")

        # -------------------------
        # 3-grams (trigrams)
        # -------------------------
        # Create all combinations of three words in forward order (i < j < k)
        # Example: [a, b, c, d] → a-b-c, a-b-d, a-c-d, b-c-d
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                for k in range(j + 1, len(words)):
                    ngrams.append(f"{words[i]}-{words[j]}-{words[k]}")

        return ngrams

    def _score_direct_results(
            self,
            raw_tags: list[str],
            query_groups: dict[str, TagGroupMeta],
            limit: int,
    ) -> tuple[dict[int, float], dict[int, list[str]]]:
        """Search Manticore for videos matching raw_tags and score each by group coverage × rarity.

        Final score is the sum of per-group contributions:
          score = Σ_g  weight_g × coverage_g × avg_rarity_g

        Scoring per group rather than across all tags prevents a large number of
        low-weight group tags from outscoring a single high-weight group match.
        Returns (scores_by_video_id, matched_tags_by_video_id).
        """
        result = self._manticore.search_tags(tags=raw_tags, limit=limit)
        scores: dict[int, float] = {}
        matched_tags: dict[int, list[str]] = {}

        for video_id, item in result.items.items():
            matched_set = set(item.matched_tags)
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
                matched_tags[video_id] = item.matched_tags

        return scores, matched_tags

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
