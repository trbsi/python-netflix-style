from django.db import models
from django.db.models import UniqueConstraint


class VideoRelationship(models.Model):
    video_id = models.BigIntegerField()
    related_video_id = models.BigIntegerField()
    similarity_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_constraints = [
            UniqueConstraint(fields=['video_id', 'related_video_id'])
        ]
