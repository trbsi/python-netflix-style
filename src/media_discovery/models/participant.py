from django.db import models

from src.media.models import VideoItem
from .tag import Tag


class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    video = models.ForeignKey(VideoItem, related_name="graph_participants", on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="participants", blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["video"]),
        ]

    def __str__(self):
        return f"Participant {self.id}"
