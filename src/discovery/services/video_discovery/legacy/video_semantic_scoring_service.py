from src.discovery.services.video_discovery.value_objects import ExpandedRelatedTags, VideoSemanticScore


class VideoSemanticScoringService:
    """
    Scores secondary semantic matches from canonical related tags.

    Direct matching remains the primary signal and is computed elsewhere with the
    existing rarity/group formula. This service only sums graph relationship
    strengths for canonical video tags that are related to the canonical query tags.
    Query tags themselves are excluded so a direct match cannot be counted again as
    a related match.
    """

    def score_semantic(
            self,
            video_canonical_tag_ids: set[int],
            expanded_tags: ExpandedRelatedTags,
    ) -> VideoSemanticScore:
        related_tag_ids = (video_canonical_tag_ids - expanded_tags.query_tag_ids) & expanded_tags.related_tag_ids

        related_score = sum(
            expanded_tags.related_scores_by_tag_id[tag_id]
            for tag_id in related_tag_ids
        )

        return VideoSemanticScore(
            related_score=related_score,
            related_tag_ids=related_tag_ids,
        )
