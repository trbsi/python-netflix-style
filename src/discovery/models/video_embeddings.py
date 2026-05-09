from django.db import models
from pgvector.django import VectorField


class VideoEmbeddings(models.Model):
    video_id = models.BigIntegerField(unique=True)
    embedding = VectorField(dimensions=384)
