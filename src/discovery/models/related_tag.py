from django.db import models

from src.discovery.models.cannonical_tag import CanonicalTag


class RelatedTag(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_tag = models.ForeignKey(
        CanonicalTag,
        on_delete=models.CASCADE,
        related_name='related_tag_sources',
    )
    target_tag = models.ForeignKey(
        CanonicalTag,
        on_delete=models.CASCADE,
        related_name='related_tag_targets',
    )
    cooccurrence_count = models.PositiveIntegerField(default=0)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['source_tag', 'target_tag'],
                name='uk_related_tag_source_target',
            ),
        ]
        indexes = [
            models.Index(fields=['source_tag', '-score'], name='related_tag_source_score_idx'),
            models.Index(fields=['target_tag', '-score'], name='related_tag_target_score_idx'),
        ]
