from django.db import models


class VideoRelationship(models.Model):
    video_id = models.BigIntegerField()
    related_video_id = models.BigIntegerField()
    similarity_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['video_id', 'related_video_id'], name='uk_video_id_related_video_id')
        ]
