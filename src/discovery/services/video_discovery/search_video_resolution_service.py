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
    TagAliasDataclass,
    CanonicalTagDataclass,
)
from src.manticore.services.manticore.manticore_search_service import ManticoreSearchService
from src.media.value_objects.search.video_tag_search_result import VideoTagSearchResult


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
        example: structured_search_query -> "black guy,cums,in,twink's ass"
        """
        grouped_words = self._to_tokens(search.structured_search_query)
        is_gay = 'gay' in search.raw_search_query
        query_groups = self._resolve_tag_into_groups(grouped_words)
        canonical_tags = [canonical_tag for canonical_tag in query_groups.keys()]

        if not canonical_tags:
            return VideoRankingResult(items=[]).get_video_ids()

        video_result = self._manticore.search_video_tags(tags=canonical_tags, is_gay=is_gay)
        direct_scores = self._score_direct_results(
            video_result=video_result,
            query_groups=query_groups,
        )

        video_ids = set(direct_scores)
        scored_videos = sorted(
            [
                VideoRankingScore(
                    video_id=video_id,
                    direct_score=direct_scores.get(video_id, 0.0),
                    final_score=direct_scores.get(video_id, 0.0),
                )
                for video_id in video_ids
            ],
            key=lambda v: v.final_score,
            reverse=True,
        )

        for vid in scored_videos:
            dump_debug(f"vid:{vid.video_id}, score: {vid.final_score}")

        return VideoRankingResult(items=scored_videos[:limit]).get_video_ids()

    def _score_direct_results(
            self,
            video_result: VideoTagSearchResult,
            query_groups: dict[str, CanonicalTagDataclass],
    ) -> dict[int, float]:
        """Search Manticore for videos matching raw_tags and score each by group coverage × rarity.

        Final score is the sum of per-group contributions:
          score = Σ_g  weight_g × coverage_g × avg_rarity_g

        Scoring per group rather than across all tags prevents a large number of
        low-weight group tags from outscoring a single high-weight group match.
        Returns (scores_by_video_id, matched_tags_by_video_id).
        """
        scores: dict[int, float] = {}

        for video_id, item in video_result.items.items():
            matched_tags_count = item.matched_tags_count
            score = 0.0

            for query_group in query_groups.values():
                group_coverage = matched_tags_count / len(query_group.tag_aliases)
                # avg_rarity = sum(m.rarity_score for m in matched_metas) / len(matched_metas)
                avg_rarity = 1
                score += query_group.weight * group_coverage * avg_rarity

            if score > 0:
                scores[video_id] = score

        return scores

    def _resolve_tag_into_groups(self, raw_tags: list[str]) -> dict[str, CanonicalTagDataclass]:
        canonical_tags = (
            TagAlias.objects
            .filter(
                raw_tag__in=raw_tags,
                canonical_tag__isnull=False,
            )
            .values_list('canonical_tag_id', flat=True)
        )
        aliases = (
            TagAlias.objects
            .select_related("canonical_tag")
            .filter(canonical_tag_id__in=list(canonical_tags))
            .only("raw_tag", "rarity_score", "canonical_tag__tag_group", "canonical_tag__slug")
        )
        alias_by_raw_tag: dict[str, TagAlias] = {alias.raw_tag: alias for alias in aliases}
        query_groups: dict[str, CanonicalTagDataclass] = {}

        for raw_tag, alias in alias_by_raw_tag.items():
            canonical_tag_group = alias.canonical_tag.tag_group
            canonical_tag_slug = alias.canonical_tag.slug
            query_group = query_groups.setdefault(
                canonical_tag_slug,
                CanonicalTagDataclass(
                    tag_group=canonical_tag_group,
                    weight=TagGroupEnum.weight(canonical_tag_group)
                )
            )
            query_group.tag_aliases.append(
                TagAliasDataclass(raw_tag=alias.raw_tag, rarity_score=alias.rarity_score)
            )

        return query_groups

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
