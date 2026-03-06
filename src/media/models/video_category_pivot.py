from django.db import models

from src.media.models import VideoCategory
from src.media.models.video_item import VideoItem


class VideoCategoryPivot(models.Model):
    video = models.ForeignKey(
        VideoItem,
        on_delete=models.CASCADE,
        related_name="video_category_links"
    )
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.CASCADE,
        related_name="video_category_links"
    )

    class Meta:
        indexes = [
            models.Index(fields=["category", "video"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['video', 'category'], name='unique_video_category'),
        ]
