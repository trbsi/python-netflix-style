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
        unique_together = ("video", "category")
        indexes = [
            models.Index(fields=["category", "video"]),
        ]
