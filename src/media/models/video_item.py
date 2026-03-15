import hashlib
import random

from django.db import models
from django.utils.text import slugify

from src.media.models import VideoCategory


class VideoItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    link = models.CharField(max_length=300)
    duration = models.PositiveIntegerField(help_text="Duration in seconds")
    thumb_small = models.TextField()
    thumb_large = models.TextField()
    embed_code = models.TextField(help_text="Raw iframe HTML")
    pub_date = models.DateTimeField()
    site = models.CharField(max_length=20)
    external_id = models.CharField(max_length=50, unique=True)
    external_created_at = models.DateField(null=True, blank=True)
    tags = models.TextField()
    categories = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    categories_relation = models.ManyToManyField(
        VideoCategory,
        through="VideoCategoryPivot",
        related_name="videos"
    )

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=["link"]),
            models.Index(fields=['external_created_at'])
        ]

    def category_slugs(self):
        array = self.categories.split(",")
        result = []
        for category in array:
            if category:
                result.append(slugify(category))

        return result

    @property
    def duration_formatted(self) -> str:
        h = self.duration // 3600
        m = (self.duration % 3600) // 60
        s = self.duration % 60

        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        return f"{m:02}:{s:02}"

    @property
    def rating(self):
        seed = self.external_id or str(self.id)
        h = hashlib.md5(seed.encode()).hexdigest()
        return 3 + (int(h, 16) % 21) / 10  # 3.0 → 5.0

    @property
    def pub_date_formatted(self):
        return self.pub_date.strftime("%b %d, %Y")

    @property
    def categories_formatted(self):
        array = self.categories.split(",")
        return ' | '.join(array)

    @property
    def categories_array(self):
        array = self.categories.split(",")
        result = []
        for category in array:
            if category:
                result.append({'title': category, 'slug': slugify(category)})

        return result

    @property
    def thumbnail_large(self):
        return random.choice(self.thumb_large.split(','))

    @property
    def thumbnail_small(self):
        return random.choice(self.thumb_small.split(','))
