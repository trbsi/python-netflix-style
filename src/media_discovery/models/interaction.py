from django.db import models

from src.media.models import VideoItem
from .participant import Participant
from .tag import Tag


class Interaction(models.Model):
    video = models.ForeignKey(
        VideoItem,
        related_name="interactions",
        on_delete=models.CASCADE,
    )

    from_participant = models.ForeignKey(
        Participant,
        related_name="outgoing_interactions",
        on_delete=models.CASCADE,
    )

    to_participant = models.ForeignKey(
        Participant,
        related_name="incoming_interactions",
        on_delete=models.CASCADE,
    )

    act = models.ForeignKey(
        Tag,
        related_name="interactions",
        on_delete=models.PROTECT,
    )

    kinks = models.ManyToManyField(
        Tag,
        related_name="kink_interactions",
        blank=True
    )
