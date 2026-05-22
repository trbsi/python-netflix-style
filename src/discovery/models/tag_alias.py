from django.db import models

from src.discovery.models.cannonical_tag import CanonicalTag


class TagAlias(models.Model):
    id = models.AutoField(primary_key=True)
    raw_tag = models.CharField(max_length=255, unique=True)
    canonical_tag = models.ForeignKey(CanonicalTag, on_delete=models.CASCADE, null=True)
    rarity_score = models.FloatField(default=0)
    tag_group = models.CharField(max_length=50, null=True)

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['canonical_tag', 'tag_group'], name='canonical_tag_tag_group_idx'),
        ]
